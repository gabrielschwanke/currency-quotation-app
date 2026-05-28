# Currency Quote Tracker

A modern and responsive currency exchange tracking platform built with **Python**, **Flask**, and **JavaScript**.

This project allows users to:

* Check exchange rates for multiple currencies and cryptocurrencies
* View historical price charts
* Analyze currency variation over the last 7, 15, or 30 days
* Access a clean and responsive interface with smooth visual effects

---

## Features

* Real-time currency exchange quotes
* Historical price charts
* Support for fiat currencies and cryptocurrencies
* Responsive modern UI
* Smooth glassmorphism design
* Interactive chart visualization
* Custom select component
* Input validation and error handling
* API-based architecture

---

## Supported Currencies

### Fiat Currencies

* USD
* EUR
* GBP
* ARS
* CAD
* JPY
* CNY

### Cryptocurrencies

* BTC
* ETH
* LTC
* DOGE

---

## Tech Stack

### Backend

* Python
* Flask
* Requests

### Frontend

* HTML5
* CSS3
* JavaScript

### APIs

* AwesomeAPI

---

## Project Structure

```bash
project/
│
├── app/
│   ├── routes.py
│   ├── services.py
│   └── templates/
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   └── js/
│       ├── chart.js
│       ├── custom-select.js
│       └── effects.js
│
├── run.py
└── requirements.txt
```

---

## Backend Overview

### `routes.py`

Responsible for:

* Route management
* Form processing
* Currency validation
* API endpoints
* Historical data responses

### `services.py`

Responsible for:

* External API communication
* Data normalization
* Timestamp formatting
* Historical data processing
* Exception handling

---

## Frontend Overview

### `chart.js`

Handles:

* Chart rendering
* Historical data visualization
* Dynamic updates
* Currency variation display

### `custom-select.js`

Handles:

* Custom select component behavior
* Improved UI interactions

### `effects.js`

Handles:

* Hover effects
* Glass card lighting effects
* Mouse interaction animations

---

## Responsive Design

The interface was designed to work smoothly on:

* Desktop
* Tablets
* Mobile devices

Using:

* CSS Grid
* Flexbox
* Media Queries

---

## Error Handling

The application includes validation and protection for:

* Invalid currencies
* Invalid dates
* API failures
* Timeout errors
* Unexpected response formats

---

## API Used

This project uses data from:

AwesomeAPI
https://docs.awesomeapi.com.br/

---

## Installation

Clone the repository:

```bash
GitHub Repository:
https://github.com/gabrielschwanke/currency-quotation-app
```

Enter the project folder:

```bash
cd currency-quotation-app
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python run.py
```

---

## Live Demo 

The application is deployed on Render:

🔗 https://currency-quotation-app.onrender.com/

## Future Improvements

* User authentication
* Favorite currencies
* Dark/light theme switch
* Currency conversion calculator
* More cryptocurrencies
* Live websocket updates

---

## License

This project is licensed under the MIT License.

---

## Author

Developed by Gabriel Pereira Schwanke.
