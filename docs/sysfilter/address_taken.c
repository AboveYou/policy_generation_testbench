#include <stdio.h>

void dummyFunction() {
    printf("Hello, function talking!\n");
}

int main() {
    // storing the address of the function
    void (*funcPtr)() = dummyFunction; 
    // calling the function via the pointer
    funcPtr(); 
    return 0;
}
