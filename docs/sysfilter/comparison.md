# Comparison
The calls which are not contained (in Sysfilter) form the approved set seen in Fuzzypol.

```bash
diff -u sysfilter/file.json.toml fuzzypol/diff.text.toml > sysfilter/file.diff
```

## diff
+4 = "stat"
+6 = "lstat"
+21 = "access"
+22 = "pipe"
+158 = "arch_prctl"

## ls
+21 = "access"
+125 = "capget"
+137 = "statfs"
+157 = "prctl"
+158 = "arch_prctl"
+191 = "getxattr"
+192 = "lgetxattr"
+218 = "set_tid_address"
+218 = "set_tid_address"

## file
+4 = "stat"
+6 = "lstat"
+21 = "access"
+22 = "pipe"
+158 = "arch_prctl"
