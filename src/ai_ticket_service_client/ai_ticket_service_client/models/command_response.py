from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.command_response_ai_result_type_0 import CommandResponseAiResultType0
    from ..models.command_response_ticket_result_type_0 import CommandResponseTicketResultType0
    from ..models.command_response_ticket_result_type_1_item import CommandResponseTicketResultType1Item


T = TypeVar("T", bound="CommandResponse")


@_attrs_define
class CommandResponse:
    """Combined AI + ticket result.

    Attributes:
        ai_result (Union['CommandResponseAiResultType0', str]):
        ticket_result (Union['CommandResponseTicketResultType0', None, list['CommandResponseTicketResultType1Item']]):
        backend_used (str):
        backend_status (str):
    """

    ai_result: Union["CommandResponseAiResultType0", str]
    ticket_result: Union["CommandResponseTicketResultType0", None, list["CommandResponseTicketResultType1Item"]]
    backend_used: str
    backend_status: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.command_response_ai_result_type_0 import CommandResponseAiResultType0
        from ..models.command_response_ticket_result_type_0 import CommandResponseTicketResultType0

        ai_result: Union[dict[str, Any], str]
        if isinstance(self.ai_result, CommandResponseAiResultType0):
            ai_result = self.ai_result.to_dict()
        else:
            ai_result = self.ai_result

        ticket_result: Union[None, dict[str, Any], list[dict[str, Any]]]
        if isinstance(self.ticket_result, CommandResponseTicketResultType0):
            ticket_result = self.ticket_result.to_dict()
        elif isinstance(self.ticket_result, list):
            ticket_result = []
            for ticket_result_type_1_item_data in self.ticket_result:
                ticket_result_type_1_item = ticket_result_type_1_item_data.to_dict()
                ticket_result.append(ticket_result_type_1_item)

        else:
            ticket_result = self.ticket_result

        backend_used = self.backend_used

        backend_status = self.backend_status

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "ai_result": ai_result,
                "ticket_result": ticket_result,
                "backend_used": backend_used,
                "backend_status": backend_status,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.command_response_ai_result_type_0 import CommandResponseAiResultType0
        from ..models.command_response_ticket_result_type_0 import CommandResponseTicketResultType0
        from ..models.command_response_ticket_result_type_1_item import CommandResponseTicketResultType1Item

        d = dict(src_dict)

        def _parse_ai_result(data: object) -> Union["CommandResponseAiResultType0", str]:
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ai_result_type_0 = CommandResponseAiResultType0.from_dict(data)

                return ai_result_type_0
            except:  # noqa: E722
                pass
            return cast(Union["CommandResponseAiResultType0", str], data)

        ai_result = _parse_ai_result(d.pop("ai_result"))

        def _parse_ticket_result(
            data: object,
        ) -> Union["CommandResponseTicketResultType0", None, list["CommandResponseTicketResultType1Item"]]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                ticket_result_type_0 = CommandResponseTicketResultType0.from_dict(data)

                return ticket_result_type_0
            except:  # noqa: E722
                pass
            try:
                if not isinstance(data, list):
                    raise TypeError()
                ticket_result_type_1 = []
                _ticket_result_type_1 = data
                for ticket_result_type_1_item_data in _ticket_result_type_1:
                    ticket_result_type_1_item = CommandResponseTicketResultType1Item.from_dict(
                        ticket_result_type_1_item_data
                    )

                    ticket_result_type_1.append(ticket_result_type_1_item)

                return ticket_result_type_1
            except:  # noqa: E722
                pass
            return cast(
                Union["CommandResponseTicketResultType0", None, list["CommandResponseTicketResultType1Item"]], data
            )

        ticket_result = _parse_ticket_result(d.pop("ticket_result"))

        backend_used = d.pop("backend_used")

        backend_status = d.pop("backend_status")

        command_response = cls(
            ai_result=ai_result,
            ticket_result=ticket_result,
            backend_used=backend_used,
            backend_status=backend_status,
        )

        command_response.additional_properties = d
        return command_response

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
