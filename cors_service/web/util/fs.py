from uuid import uuid4


def get_temp_file_path() -> str:
    """Get a file path that can be used for a temporary file."""
    # TODO make this work for all platforms
    return "/tmp/" + str(uuid4())
