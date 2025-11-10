from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.chat_completion_response_usage import ChatCompletionResponseUsage
    from ..models.chat_message import ChatMessage


T = TypeVar("T", bound="ChatCompletionResponse")


@_attrs_define
class ChatCompletionResponse:
    """Response model for chat completion.

    Attributes:
        message (ChatMessage): A single message in a chat conversation.
        model (str): The model used for generation
        usage (ChatCompletionResponseUsage): Token usage information
        finish_reason (Union[None, Unset, str]): Reason for completion
    """

    message: "ChatMessage"
    model: str
    usage: "ChatCompletionResponseUsage"
    finish_reason: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        message = self.message.to_dict()

        model = self.model

        usage = self.usage.to_dict()

        finish_reason: Union[None, Unset, str]
        if isinstance(self.finish_reason, Unset):
            finish_reason = UNSET
        else:
            finish_reason = self.finish_reason

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "message": message,
                "model": model,
                "usage": usage,
            }
        )
        if finish_reason is not UNSET:
            field_dict["finish_reason"] = finish_reason

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.chat_completion_response_usage import ChatCompletionResponseUsage
        from ..models.chat_message import ChatMessage

        d = dict(src_dict)
        message = ChatMessage.from_dict(d.pop("message"))

        model = d.pop("model")

        usage = ChatCompletionResponseUsage.from_dict(d.pop("usage"))

        def _parse_finish_reason(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        finish_reason = _parse_finish_reason(d.pop("finish_reason", UNSET))

        chat_completion_response = cls(
            message=message,
            model=model,
            usage=usage,
            finish_reason=finish_reason,
        )

        chat_completion_response.additional_properties = d
        return chat_completion_response

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
