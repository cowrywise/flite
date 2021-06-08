from flite.reviewer import ReviewerMixin
import math


class TransferManager(ReviewerMixin):
    """the order of these checks matter"""

    def __init__(self, sender, receiver, amount):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount

    def check_transfer_to_self(self):
        if self.sender == self.receiver:
            return {"success": False, "message": "cannot make a transfer to self"}
        return {"success": True, "message": ""}

    def check_amount(self):
        if math.floor(self.amount) == 0:
            return {
                "success": False,
                "message": "please enter amount greater than or equal to 1",
            }
        return {"success": True, "message": ""}
