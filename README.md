# GPS Anomaly Detection

## Description
This project automates the process of detecting and correcting anomalous GPS coordinates using AI-generated C++ algorithms. The system interacts with OpenAI's API to generate, test, and iteratively improve algorithms for identifying and fixing GPS data anomalies (like "GPS spikes") through interpolation.

The solution processes JSON files containing GPS coordinates (latitude, longitude) with timestamps, identifies outliers, and replaces them with theoretically correct values.

## Key Features
AI-powered algorithm generation via OpenAI API

Automatic C++ code compilation and testing

Iterative improvement process

Performance metrics collection

Support for multiple test datasets

## Prerequisites
Python 3.x

OpenAI Python module (pip install openai)

OpenAI API key set in environment variables (OPENAI_API_KEY)

g++ compiler installed and available in PATH

## Possible improvements 

Currently, one correct algorithm was achieved in a single run of the script. Better results can likely be obtained by: improving the script, refining the prompts, adjusting the temperature, increasing amount of iterations, or trying different models.

## Current best result
<img width="2000" height="600" alt="points_comparsion" src="https://github.com/user-attachments/assets/16a7ca9c-9934-4a8d-8ae4-9e1324bd96e3" />
 
