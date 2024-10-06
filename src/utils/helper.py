import datetime


def print_with_timestamp(message):
    """Prints a message with the current timestamp.

  Args:
    message: The message to be printed.
  """

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} : {message}")
