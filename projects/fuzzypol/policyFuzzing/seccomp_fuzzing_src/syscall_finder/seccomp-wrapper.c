#define _DEFAULT_SOURCE
#include <dirent.h>
#include <seccomp.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/prctl.h>
#include <unistd.h>

/* This function returns the path to the highest number filter file of the binary name in the filters directory */
char* getPath(char *fname) {
  char dirname[32];
  char *path = malloc(64 * sizeof(char));
  char *end;
  int n, tmp;
  struct dirent **filelist;

  /* Generate the directory name */
  snprintf(dirname, sizeof(dirname), "/tmp/syscall-finder/%s", fname);
  /* Scan the directory for a list of files */
  n = scandir(dirname, &filelist, NULL, alphasort);

  /* Return if there's an error */
  if (n == -1) {
    perror("scandir");
    return "0";
  }

  /* Only check through it if there's more than two files, since the should always be at least two directories, . and .. */
  if (n > 2) {
    /* Create the array for all file names, since they are numbers it can be ints */
    int arr[n];

    /* write the directory name into the array, unless it's . and .. then just put -1 
    free memory after */
    while (n--) {
      if (strcmp(filelist[n]->d_name, ".") == 0 || strcmp(filelist[n]->d_name, "..") == 0) {
        arr[n] = -1;
      } else {
        tmp = strtol(filelist[n]->d_name, &end, 10);
        arr[n] = tmp;
      }
      free(filelist[n]);
    }
    free(filelist);

    /* Find the biggest number in the array */
    tmp = 0;
    for (n = 0; n < sizeof(arr) / sizeof(int); n++) {
      if (tmp < arr[n]) tmp = arr[n];
    }
  } else {
    while (n--) {
      free(filelist[n]);
    }
    free(filelist);
    tmp = 0;
  }
  
  /* Generate the path to the file and return it */
  snprintf(path, 64, "%s/%d", dirname, tmp);
  printf("filter path: %s\n", path);
  return path;
}

int main(int argc, char **argv) {
  int c, rc, rc2, syscall = 0;
  char *fpath;
  FILE* filter;
  scmp_filter_ctx ctx86 = NULL;
  scmp_filter_ctx ctx86_64 = NULL;

  if (argc < 4) {
    printf("Usage: %s <log|kill> <binary name> <absolute path to binary> [<binary args>]\n", argv[0]);
    return -1;
  }

  // SECCOMP_SET_MODE_FILTER won't work unless you run it with CAP_SYS_ADMIN or set this bit
  prctl(PR_SET_NO_NEW_PRIVS, 1);

  // create filter for both architectures
  if (0 == strcmp(argv[1], "log")) {
    ctx86 = seccomp_init(SCMP_ACT_LOG);
    if (!ctx86) {
      perror("initializing filter");
    }
  } else if (0 == strcmp(argv[1], "kill")) {
    ctx86 = seccomp_init(SCMP_ACT_KILL_PROCESS);
    ctx86_64 = seccomp_init(SCMP_ACT_KILL_PROCESS);

    if (!ctx86 || !ctx86_64) {
      perror("initializing filters");
      return -2;
    }

    // set archs of filters accordingly, can be extended with others
    // remove native arch first
    seccomp_arch_remove(ctx86, SCMP_ARCH_NATIVE);
    seccomp_arch_remove(ctx86_64, SCMP_ARCH_NATIVE);
    // add b64 and b32 archs
    seccomp_arch_add(ctx86, SCMP_ARCH_X86);
    seccomp_arch_add(ctx86_64, SCMP_ARCH_X86_64);

    // add rules
    /* 59 for execve in this wrapper and exit_group for graceful termination */
    seccomp_rule_add(ctx86_64, SCMP_ACT_ALLOW, 59, 0); // execve
    seccomp_rule_add(ctx86_64, SCMP_ACT_ALLOW, 231, 0); // sys_exit_group

    // add rules from filter file
    // getPath returns the path /filters/binary-name/highest-number-filter
    fpath = getPath(argv[2]);
    // getPath returns "0" if no filter has been found
    if (0 != strcmp(fpath, "0")) {
      filter = fopen(fpath, "r");
      free(fpath);
      if (filter == NULL) {
        perror("opening filter");
      } else {
        do {
          c = fgetc(filter);
          if (feof(filter)) break;
          switch(c) {
            case '0':
              break;
            case '1':
              seccomp_rule_add(ctx86, SCMP_ACT_ALLOW, syscall, 0);
              break;
            case '2':
              seccomp_rule_add(ctx86_64, SCMP_ACT_ALLOW, syscall, 0);
              break;
            case '3':
              seccomp_rule_add(ctx86, SCMP_ACT_ALLOW, syscall, 0);
              seccomp_rule_add(ctx86_64, SCMP_ACT_ALLOW, syscall, 0);
              break;
            default:
              break;
          }
          syscall++;
        } while(1);
        fclose(filter);
      }  
    }
    
    // merge filters into one
    if (seccomp_merge(ctx86, ctx86_64)) {
      perror("merge");
      return -3;
    }

    // enable bit that makes seccomp log all actions except for passing syscalls (ALLOW)
    rc2 = seccomp_attr_set(ctx86, SCMP_FLTATR_CTL_LOG, 1);
    if (rc2 < 0) {
      perror("attr_set");
    }
  } else {
    printf("Usage: %s <log|kill> <binary name> <absolute path to binary> [<binary args>]\n", argv[0]);
    return -4;
  }

  // load the filter
  rc = seccomp_load(ctx86);
  if (rc != 0) goto out;

  // start program to be filtered
  execv(argv[3], &argv[3]);
out:
  // release the filter from memory
  seccomp_release(ctx86);
  return rc;
}