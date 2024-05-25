from datetime import datetime

def convert_unix_to_datetime(unix_timestamp):
    print(f"Converting Unix timestamp: {unix_timestamp}")
    # Print the type of unix_timestamp
    print(type(unix_timestamp))
    try:
        # Ensure the input is a valid integer representing Unix time
        if isinstance(unix_timestamp, str):
            if unix_timestamp.isdigit():
                unix_timestamp = int(unix_timestamp)
            else:
                # Check if it's already a datetime string in the correct format
                try:
                    datetime.strptime(unix_timestamp, '%Y-%m-%d %H:%M:%S')
                    return unix_timestamp
                except ValueError:
                    raise ValueError("Invalid Unix timestamp format")
        elif isinstance(unix_timestamp, int):
            pass
        else:
            raise ValueError("Invalid Unix timestamp format")
        
        return datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        # Print the error and return None
        print(f"Error: {e}")
        return None

# Example usage
print(convert_unix_to_datetime(1716607008))
print(convert_unix_to_datetime("1716607008"))
print(convert_unix_to_datetime("2024-05-24 23:16:48"))
print(convert_unix_to_datetime("invalid_timestamp"))
