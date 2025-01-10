from pydantic import BaseModel
from er_explorer.erd import serve

class Project(BaseModel):
    id: int
    name: str

class Team(BaseModel):
    id: int
    name: str


class Event(BaseModel):
    id: int
    name: str

class Milestone(BaseModel):
    id: int
    name: str

class ProjectChangeLog(BaseModel):
    id: int
    content: str

class MeetingNote(BaseModel):
    id: int
    title: str
    content: str

class MeetingNoteAttendee(BaseModel):
    id: int
    name: str

class MeetingNoteFollowup(BaseModel):
    id: int
    name: str

class Service(BaseModel):
    id: int
    name: str

class ServiceAdopt(BaseModel):
    id: int
    name: str

definitions = [
    dict(source=Project, target=Event, field='owns'),
    dict(source=Project, target=Milestone, field='owns'),
    dict(source=Project, target=ProjectChangeLog, field='generate'),
    dict(source=Project, target=MeetingNote, field='owns'),
    dict(source=MeetingNote, target=MeetingNoteAttendee, field='has'),
    dict(source=MeetingNote, target=MeetingNoteFollowup, field='has'),
    dict(source=Team, target=Service, field='manage'),
    dict(source=Project, target=ServiceAdopt, field='has'),
    dict(source=Service, target=ServiceAdopt, field='belong'),
]

serve(definitions)