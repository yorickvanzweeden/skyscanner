# Skyscanner scraper

If you happen to stumble across this repository, no guarantees it will work in the future. Skyscanner may update their DOM tree.

## How it works
This repo contains a FastAPI server with a TamperMonkey script. The FastAPI server manages the to-be-processed and processed flight data, whilst the TamperMonkey script fetches the next flight to be processed, and sends retrieved data to the FastAPI server. You can run the TamperMonkey script in multiple windows to speed up the process.

## How to use it
1. Create a config.json that specifies all your legs. Be sure that you do not create too many options, as all permutations will be checked. It multiplies very quickly
2. Install dependencies using poetry
3. Run the FastAPI server using `poetry run python main.py`
4. Install the TamperMonkey script in your browser. It will fetch the next unknown flight and send it to the FastAPI server
5. If all data is collected (in data.json), you can convert it into an Excel sheet using `poetry run python flights_to_excel.py`

The json output looks like
```json
    {
        "start_airport": "DXB",
        "end_airport": "KUL",
        "fly_date": "2024-01-28T00:00:00",
        "price": 212.0,
        "stops": 1,
        "start_time": "2024-01-28T23:10:00Z",
        "end_time": "2024-01-29T14:30:00Z"
    }
```

## How you could improve the repo
- Add a database to store the data rather than a JSON file
- Add a frontend to view the data
- Add checks to make sure you don't create too many permutations
