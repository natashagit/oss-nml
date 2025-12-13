from collections.abc import Mapping
from typing import Any, TypeVar, Union

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CommandRequest")


@_attrs_define
class CommandRequest:
    """Incoming natural language command for ticket creation.

    Attributes:
        user_input (str):
        system_prompt (Union[Unset, str]):  Default: 'You are a strict router that extracts intent, title,
            description.'.
        backend (Union[Unset, str]):  Default: 'google_tasks'.
    """

    user_input: str
    system_prompt: Union[Unset, str] = "You are a strict router that extracts intent, title, description."
    backend: Union[Unset, str] = "google_tasks"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        user_input = self.user_input

        system_prompt = self.system_prompt

        backend = self.backend

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "user_input": user_input,
            }
        )
        if system_prompt is not UNSET:
            field_dict["system_prompt"] = system_prompt
        if backend is not UNSET:
            field_dict["backend"] = backend

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        user_input = d.pop("user_input")

        system_prompt = d.pop("system_prompt", UNSET)

        backend = d.pop("backend", UNSET)

        command_request = cls(
            user_input=user_input,
            system_prompt=system_prompt,
            backend=backend,
        )

        command_request.additional_properties = d
        return command_request

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
