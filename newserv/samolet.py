from datetime import datetime

def check_flight_status(schedule_time, actual_time):

    schedule_time = datetime.strptime(schedule_time, "%H:%M")
    actual_time = datetime.strptime(actual_time, "%H:%M")

    # Рассчитываем разницу во времени
    time_difference = actual_time - schedule_time

    # Определяем статус прилета
    if time_difference.total_seconds() > 0:
        return f"Самолет опаздывает. Задержка: {time_difference}"
    elif time_difference.total_seconds() < 0:
        return f"Самолет прилетел раньше. Опережение: {-time_difference}"
    else:
        return "Самолет прилетел вовремя."


schedule_time_input = input("Введите время прибытия по расписанию (в формате ЧЧ:ММ): ")
actual_time_input = input("Введите фактическое время прибытия (в формате ЧЧ:ММ): ")

try:
    result = check_flight_status(schedule_time_input, actual_time_input)

    print(result)
except Exception as e:
    print(e)

# import unittest

# class TestFlightStatus(unittest.TestCase):
#     def test_delayed_flight(self):
#         schedule_time = "12:00"
#         actual_time = "12:15"
#         result = check_flight_status(schedule_time, actual_time)
#         self.assertIn("Самолет опаздывает", result)

#     def test_early_flight(self):
#         schedule_time = "12:00"
#         actual_time = "11:45"
#         result = check_flight_status(schedule_time, actual_time)
#         self.assertIn("Самолет прилетел раньше", result)

#     def test_on_time_flight(self):
#         schedule_time = "12:00"
#         actual_time = "12:00"
#         result = check_flight_status(schedule_time, actual_time)
#         self.assertIn("Самолет прилетел вовремя", result)

# if __name__ == '__main__':
#     unittest.main()
