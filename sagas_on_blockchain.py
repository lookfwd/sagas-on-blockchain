import unittest

debug = False


class Account(object):
    def __init__(self, quantity, min_price, percent):
        self.quantity = quantity
        self.min_price = min_price
        self.percent = percent

    def book_budget(self, days, budget):
        if self.quantity <= 0:
            return -1
        price = (budget * self.percent) // 100
        min_price = self.spot_price(days)
        if price < min_price:
            return -1
        self.quantity -= 1
        return price

    def book_spot(self, days):
        if self.quantity <= 0:
            return -1
        price = self.spot_price(days)
        self.quantity -= 1
        return price

    def spot_price(self, days):
        return self.min_price * days

    def do_return(self):
        self.quantity += 1


class CarRental(Account):
    def __init__(self, cars, price):
        super(CarRental, self).__init__(cars, price, 20)


class Booking(Account):
    def __init__(self, hotels, price):
        super(Booking, self).__init__(hotels, price, 70)


class Blockchain(object):
    def __init__(self):
        self.contracts = {}

    def register_contract(self, name, what):
        self.contracts[name] = what

    def run_contract(self, contract, arguments):
        days = arguments["days"]
        error = None
        for i in contract.split("\n"):
            i = i.strip()
            if not i:
                continue
            if i == "def book_on_budget(days, budget):":
                budget = arguments["budget"]
            elif i == "def book(days):":
                pass
            elif i == "car = bookCar(days, budget)":
                car_fee = self.contracts["bookCar(days, budget)"](days, budget)
                if debug:
                    print "car_fee: {}".format(car_fee)
            elif i == "car = bookCar(days)":
                car_fee = self.contracts["bookCar(days)"](days)
                if debug:
                    print "car_fee: {}".format(car_fee)
            elif i == "if not car:":
                error = (car_fee == -1)
            elif i == "if not hotel:":
                error = (hotel_fee == -1)
            elif i == "return -1":
                assert error is not None
                if error:
                    if debug:
                        print "Error"
                    return -1
                error = None
                if debug:
                    print "OK"
            elif i == "budget -= car.fee":
                budget -= car_fee
                if debug:
                    print "budget_after: {}".format(budget)
            elif i == "hotel -= bookHotel(days, budget)":
                hotel_fee = self.contracts["bookHotel(days, budget)"](days,
                                                                      budget)
                if debug:
                    print "hotel_fee: {}".format(hotel_fee)
            elif i == "hotel = bookHotel(days)":
                hotel_fee = self.contracts["bookHotel(days)"](days)
                if debug:
                    print "hotel_fee: {}".format(hotel_fee)
            elif i == "returnCar()":
                if error:
                    self.contracts["returnCar()"]()
            elif i == "return budget - hotel.fee":
                change = budget - hotel_fee
                return change
            elif i == "return car.fee + hotel.fee":
                return car_fee + hotel_fee
            else:
                assert False, "unknown command: {}".format(i)


def broker_book_me_vacations_on_budget(bc, days, budget):
    contract = """
    def book_on_budget(days, budget):
        car = bookCar(days, budget)
        if not car:
            return -1
        budget -= car.fee
        hotel -= bookHotel(days, budget)
        if not hotel:
            returnCar()
            return -1
        return budget - hotel.fee
    """
    return bc.run_contract(contract, {"days": days, "budget": budget})


def broker_book_me_vacations(bc, days):
    contract = """
    def book(days):
        car = bookCar(days)
        if not car:
            return -1
        hotel = bookHotel(days)
        if not hotel:
            returnCar()
            return -1
        return car.fee + hotel.fee
    """
    return bc.run_contract(contract, {"days": days})


class TestBlockchain(unittest.TestCase):

    def test_simple(self):
        bc = Blockchain()

        car = CarRental(2, 50)
        bc.register_contract("bookCar(days, budget)", car.book_budget)
        bc.register_contract("bookCar(days)", car.book_spot)
        bc.register_contract("returnCar()", car.do_return)

        booking = Booking(30, 400)
        bc.register_contract("bookHotel(days, budget)", booking.book_budget)
        bc.register_contract("bookHotel(days)", booking.book_spot)
        bc.register_contract("returnHotel()", booking.do_return)

        if debug:
            print "-- STEP1 --"
        change = broker_book_me_vacations_on_budget(bc, 3, 1000)
        self.assertEquals(change, -1)

        if debug:
            print "-- STEP2 --"
        change = broker_book_me_vacations_on_budget(bc, 3, 2400)
        self.assertEquals(change, 576)

        if debug:
            print "-- STEP3 --"
        amount = broker_book_me_vacations(bc, 3)
        self.assertEquals(amount, 1350)

        if debug:
            print "-- STEP4 --"
        amount = broker_book_me_vacations(bc, 3)
        self.assertEquals(amount, -1)

if __name__ == '__main__':
    unittest.main()
