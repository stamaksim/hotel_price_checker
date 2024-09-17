from types import TracebackType
from typing import Type
import pytest
import json
from main import (
    load_data,
    find_cheapest_room,
    calculate_total_prices,
    save_results_to_file
)


def test_load_data(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test if load_data correctly loads data from a JSON file."""

    mock_data = {
        "assignment_results": [
            {
                "shown_price": {"Single Room": "50"},
                "ext_data": {"taxes": '{"tax": "5"}'},
                "number_of_guests": 1,
            }
        ]
    }

    class MockFile:
        def __init__(self, data: dict) -> None:
            self.data = data

        def __enter__(self) -> 'MockFile':
            return self

        def __exit__(
                self, exc_type: Type[BaseException],
                exc_value: BaseException,
                traceback: 'TracebackType'
        ) -> None:
            pass

        def read(self) -> str:
            return json.dumps(self.data)

    def mock_open(*args: str, **kwargs: dict) -> MockFile:
        return MockFile(mock_data)

    # Replace the open function with the mock_open function
    monkeypatch.setattr("builtins.open", mock_open)

    results = load_data("prices.json")

    assert results == mock_data["assignment_results"]


def test_find_cheapest_room() -> None:
    """Test if find_cheapest_room correctly finds the cheapest room."""

    test_data = [
        {
            "shown_price": {"Single Room": "50", "Double Room": "75"},
            "ext_data": {"taxes": '{"tax": "5"}'},
            "number_of_guests": 1,
        },
        {
            "shown_price": {"Single Room": "45", "Double Room": "80"},
            "ext_data": {"taxes": '{"tax": "10"}'},
            "number_of_guests": 2,
        },
    ]

    result = find_cheapest_room(test_data)

    assert result["cheapest_price"] == 45
    assert result["cheapest_room"]["room_type"] == "Single Room"
    assert result["cheapest_room"]["guests"] == 2


def test_calculate_total_prices() -> None:
    """
    Test if calculate_total_prices correctly calculates the total prices.
    """

    test_data = [
        {
            "shown_price": {"Single Room": "50", "Double Room": "75"},
            "ext_data": {"taxes": '{"tax": "5"}'},
            "number_of_guests": 1,
        }
    ]

    total_prices = calculate_total_prices(test_data)

    assert total_prices[0]["room_type"] == "Single Room"
    assert total_prices[0]["total_price"] == 55.0  # 50 + 5
    assert total_prices[1]["room_type"] == "Double Room"
    assert total_prices[1]["total_price"] == 80.0  # 75 + 5


def test_save_results_to_file(tmpdir: pytest.TempdirFactory) -> None:
    """Test if results are correctly saved to a file in a table format."""

    cheapest_room = {
        "cheapest_price": 50,
        "cheapest_room": {"room_type": "Single Room", "guests": 1},
    }

    total_prices = [
        {"room_type": "Single Room", "total_price": 55.0},
        {"room_type": "Double Room", "total_price": 80.0},
    ]

    mock_output_file = tmpdir.join("lower_price.txt")
    save_results_to_file(
        str(mock_output_file),
        cheapest_room, total_prices
    )

    with open(mock_output_file) as file:
        content = file.read()

    assert "Cheapest price: 50" in content
    assert "Room type: Single Room, Guests: 1" in content
    assert "Total prices for all rooms:" in content
    assert "+-------------+---------------+" in content
    assert "| Room Type   |   Total Price |" in content
    assert "+=============+===============+" in content
    assert "| Single Room |            55 |" in content
    assert "| Double Room |            80 |" in content
    assert "+-------------+---------------+" in content
