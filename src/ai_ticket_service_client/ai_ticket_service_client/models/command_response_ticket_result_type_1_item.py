from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CommandResponseTicketResultType1Item")


@_attrs_define
class CommandResponseTicketResultType1Item:
    """Individual item in a ticket result list (Type 1 variant).

    This class represents an individual item when ticket_result is a list in CommandResponse.
    The ticket_result field is a union type that can be a single object (Type0), None, or a list (Type1).
    Type1Item is used when the ticket operation returns multiple tickets (e.g., search results).

    """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        command_response_ticket_result_type_1_item = cls()

        command_response_ticket_result_type_1_item.additional_properties = d
        return command_response_ticket_result_type_1_item

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
