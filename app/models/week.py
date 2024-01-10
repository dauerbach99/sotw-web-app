from typing import List
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.response import Response


class Week(Base):

    id: Mapped[int] = mapped_column(primary_key=True)
    week_num: Mapped[int]
    playlist_link: Mapped[str]
    sotw_id: Mapped[int] = mapped_column(ForeignKey('sotw.id'))
    survey_release: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    results_release: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    responses: Mapped[List[Response]] = relationship(back_populates='week')