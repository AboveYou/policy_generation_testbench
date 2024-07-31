#include <stdio.h>

void functionA() {
    printf("Inside functionA\n");
}

void functionB() {
    printf("Inside functionB\n");
    functionA();
}

void functionC() {
    printf("Inside functionC\n");
    functionB();
}

int main() {
    functionC();
    return 0;
}
