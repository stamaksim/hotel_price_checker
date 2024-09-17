import json
from typing import List, Dict, Any
from tabulate import tabulate


def load_data(filepath: str) -> List[Dict[str, Any]]:
    """Load JSON data from the file."""
    try:
        with open(filepath, "r") as file:
            data = json.load(file)
        return data.get("assignment_results", [])
    except FileNotFoundError:
        raise FileNotFoundError(
            f"The file {filepath} does not exist."
        )
    except json.JSONDecodeError:
        raise ValueError(
            f"Error decoding JSON from the file {filepath}."
        )


def find_cheapest_room(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Finds the cheapest room from the provided data."""
    cheapest_price = float("inf")
    cheapest_room = None

    for result in results:
        shown_prices = result.get("shown_price", {})
        for room_type, net_price in shown_prices.items():
            net_price = float(net_price)
            if net_price < cheapest_price:
                cheapest_price = net_price
                cheapest_room = {
                    "room_type": room_type,
                    "guests": result.get("number_of_guests", "N/A"),
                }

    return {
        "cheapest_price": cheapest_price,
        "cheapest_room": cheapest_room,
    }


def calculate_total_prices(
        results: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Calculates the total price (net price + taxes) for each room."""
    total_price_data = []

    for result in results:
        shown_prices = result.get("shown_price", {})
        taxes = json.loads(result["ext_data"]["taxes"])
        total_taxes = sum(float(value) for value in taxes.values())

        for room_type, net_price in shown_prices.items():
            net_price = float(net_price)
            total_price = round(net_price + total_taxes, 2)
            total_price_data.append(
                {"room_type": room_type, "total_price": total_price}
            )

    return total_price_data


def print_cheapest_room(data: Dict[str, Any]) -> None:
    """Prints the cheapest room information."""
    print(f"Cheapest price: {data['cheapest_price']}")
    print(
        f"Room type: {data['cheapest_room']['room_type']}, "
        f" Guests: {data['cheapest_room']['guests']}"
    )


def print_total_prices(data: List[Dict[str, Any]]) -> None:
    """Prints total prices for all rooms in a table format."""
    table = []
    for room in data:
        table.append([room['room_type'], room['total_price']])
    headers = ["Room Type", "Total Price"]
    print("Total prices for all rooms:")
    print(tabulate(table, headers=headers, tablefmt="grid"))


def save_results_to_file(
    filepath: str,
    cheapest_room: Dict[str, Any],
    total_prices: List[Dict[str, Any]],
) -> None:
    """Saves the results to a file in a table format."""
    with open(filepath, "w") as file:
        file.write(f"Cheapest price: {cheapest_room['cheapest_price']}\n")
        file.write(
            f"Room type: {cheapest_room['cheapest_room']['room_type']},"
            f" Guests: {cheapest_room['cheapest_room']['guests']}\n"
        )
        file.write("Total prices for all rooms:\n")
        headers = ["Room Type", "Total Price"]
        table = []
        for room in total_prices:
            table.append([room['room_type'], room['total_price']])
        file.write(tabulate(table, headers=headers, tablefmt="grid"))


# Example usage:
if __name__ == "__main__":
    filepath = "prices.json"
    results = load_data(filepath)

    cheapest_room = find_cheapest_room(results)
    total_prices = calculate_total_prices(results)

    print_cheapest_room(cheapest_room)
    print_total_prices(total_prices)
    save_results_to_file("lower_price.txt", cheapest_room, total_prices)
