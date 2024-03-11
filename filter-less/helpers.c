#include "helpers.h"
#include <math.h>

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int average = (int) ((image[i][j].rgbtBlue + image[i][j].rgbtGreen + image[i][j].rgbtRed) / 3.0 + 0.5);

            image[i][j].rgbtBlue = average;
            image[i][j].rgbtRed = average;
            image[i][j].rgbtGreen = average;
        }
    }
}

// Convert image to sepia
void sepia(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int originalRed = image[i][j].rgbtRed;
            int originalGreen = image[i][j].rgbtGreen;
            int originalBlue = image[i][j].rgbtBlue;

            image[i][j].rgbtRed = fmin(255, (int) (0.393 * originalRed + 0.769 * originalGreen + 0.189 * originalBlue + 0.5));
            image[i][j].rgbtGreen = fmin(255, (int) (0.349 * originalRed + 0.686 * originalGreen + 0.168 * originalBlue + 0.5));
            image[i][j].rgbtBlue = fmin(255, (int) (0.272 * originalRed + 0.534 * originalGreen + 0.131 * originalBlue + 0.5));
        }
    }
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width / 2; j++) // Note: Loop only until the middle column
        {
            RGBTRIPLE temp = image[i][j];
            image[i][j] = image[i][width - 1 - j];
            image[i][width - 1 - j] = temp;
        }
    }
}

// Blur image
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    RGBTRIPLE temp[height][width]; // Create a temporary array to store blurred values

    // Copy original image to the temporary array
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            temp[i][j] = image[i][j];
        }
    }

    // Apply the blur filter
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int totalRed = 0, totalGreen = 0, totalBlue = 0; // Initialize variables to store sum of color values
            float counter = 0.00; // Initialize counter to keep track of neighboring pixels

            // Loop through surrounding pixels in a 3x3 grid
            for (int x = -1; x < 2; x++)
            {
                for (int y = -1; y < 2; y++)
                {
                    int currentX = i + x; // Calculate the X-coordinate of the current surrounding pixel
                    int currentY = j + y; // Calculate the Y-coordinate of the current surrounding pixel

                    // Check if the surrounding pixel is within the image boundaries
                    if (currentX < 0 || currentX > (height - 1) || currentY < 0 || currentY > (width - 1))
                    {
                        continue; // Skip if the surrounding pixel is outside the image
                    }

                    // Add the color values of the surrounding pixel to the totals
                    totalRed += image[currentX][currentY].rgbtRed;
                    totalGreen += image[currentX][currentY].rgbtGreen;
                    totalBlue += image[currentX][currentY].rgbtBlue;

                    counter++; // Increment the counter for each valid surrounding pixel
                }
            }

            // Calculate the average color values for the current pixel and update the temporary array
            temp[i][j].rgbtRed = round(totalRed / counter);
            temp[i][j].rgbtGreen = round(totalGreen / counter);
            temp[i][j].rgbtBlue = round(totalBlue / counter);
        }
    }

    // Copy the blurred values from the temporary array back to the original image
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            image[i][j] = temp[i][j];
        }
    }

    return; // Return the blurred image
}
