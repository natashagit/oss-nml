from collections.abc import Mapping
from typing import Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="CommandResponseTicketResultType0")


@_attrs_define
class CommandResponseTicketResultType0:
    """Ticket result as a single object (Type 0 variant).

    This class represents the single object variant of the ticket_result field in CommandResponse.
    The ticket_result field is a union type that can be a single object (Type0), None, or a list (Type1).
    Type0 is used when the ticket operation returns a single ticket object (e.g., get, create, update).

    """

    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        command_response_ticket_result_type_0 = cls()

        command_response_ticket_result_type_0.additional_properties = d
        return command_response_ticket_result_type_0

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
