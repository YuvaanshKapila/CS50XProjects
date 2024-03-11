#include <cs50.h>
#include <stdio.h>

int main(void)
{
    // Get a string input from the user
    string name = get_string("What's your name?\n");

    // Print a personalized greeting
    printf("Hello, %s!\n", name);
}
