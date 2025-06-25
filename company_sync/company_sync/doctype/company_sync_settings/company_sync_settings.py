# Copyright (c) 2025, Dante Devenir and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document


class CompanySyncSettings(Document):
    from typing import TYPE_CHECKING
    if TYPE_CHECKING:
        user_api: str  # DF.Data
        endpoint: str  # DF.Data
