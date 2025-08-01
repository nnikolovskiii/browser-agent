from typing import List, Literal

from pydantic import BaseModel, Field


class SearchFilePathsList(BaseModel):
    file_paths: List[str] = Field(
        description="A list of file paths that should be searched."
    )
    rationale: str = Field(
        description="A brief explanation of why these file_paths could prove relevant to the user's task."
    )


class FileReflectionList(BaseModel):
    additional_file_paths: List[str] = Field(
        description="A list of file paths that should be added to the context on top of the existing ones."
    )
    remove_file_paths: List[str] = Field(
        description="A list of file paths that should be removed from the context."
    )


class EnhanceTextInstruction(BaseModel):
    enhance_user_message: str = Field(
        description="User message that is made clearer."
    )
    language: str = Field(
        description="The language of the input: alb, mkd or eng."
    )


class Route(BaseModel):
    step: Literal["about_me", "info", "not_suitable"] = Field(
        None, description="The next step in the routing process"
    )
    rationale: str = Field(
        description="A brief explanation of why these file_paths could prove relevant to the user's task."
    )


class InputType(BaseModel):
    input_type: Literal["question", "task"] = Field(
        description="Determination of whether the user input is a question or a task."
    )
