# Product Recommendation Chatbot

A smart chatbot that provides product recommendations based on user preferences using OpenAI's GPT model and PostgreSQL database.

## Features

- Natural language understanding of user preferences
- Product recommendations based on multiple criteria:
  - Price range
  - Color preferences
  - Performance specifications (max speed, consumption)
- RESTful API endpoint for chat interactions
- PostgreSQL database integration

## Prerequisites

- Python 3.8+
- PostgreSQL database
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd <repository-name>
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key
   - Configure your PostgreSQL database URL

5. Set up the database:
   - Create a PostgreSQL database
   - Run the schema.sql file:
```bash
psql -U your_username -d your_database_name -f schema.sql
```

## Running the Application

Start the FastAPI server:
```bash
python chatbot.py
```

The server will start at `http://localhost:8000`

## API Usage

Send a POST request to `/chat` endpoint with the following JSON structure:

```json
{
    "messages": [
        {
            "role": "user",
            "content": "I'm looking for a red sports car under $70,000 with good fuel efficiency"
        }
    ]
}
```

## Example Queries

- "Show me cars under $50,000"
- "I want a red sports car with max speed over 200"
- "Find me an eco-friendly vehicle with low consumption"
- "What are the best family cars in silver color?"

## Prompt Templates

Prompt templates for the LLM are stored in the `prompts/` directory and rendered using Jinja2 for maintainability and flexibility. You can edit these files to update the system or user prompts without changing the code.

## Contributing

Feel free to submit issues and enhancement requests! # CarSalebot0.2
