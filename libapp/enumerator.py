from aenum import Enum

NodeTypes = Enum("NodeTypes", "article, blog, page, team, testimonials")
SpaceStatus = Enum("Status", "Incomplete, Duplicate, Waiting, Published, Revoked, Filled,                        Unpublished, Unresponse, Blocked, Test, Spam")
