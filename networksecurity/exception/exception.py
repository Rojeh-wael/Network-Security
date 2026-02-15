import sys
from networksecurity.logging import logger
from networksecurity.logging.logger import logging

class NetworkSecurityException(Exception):
    def __init__(self, message, error_detail: sys):
        super().__init__(message)
        self.error_detail = error_detail

    def __str__(self):
        return f"{self.error_detail}: {super().__str__()}"
    
if __name__ == "__main__":
    try:
        logger.logging.info("This is an info message")
        raise NetworkSecurityException("This is a network security exception", sys)
    except NetworkSecurityException as e:
        print(e)