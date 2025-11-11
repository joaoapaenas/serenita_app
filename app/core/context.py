# app/core/context.py
from dataclasses import dataclass

from app.services.interfaces import (
    ICycleService, ISessionService, IExamService, IUserService, IPerformanceService,
    IAnalyticsService, IMasterSubjectService, ICycleSubjectService, IStudyQueueService,
    IWorkUnitService, ITemplateSubjectService
)


@dataclass
class AppContext:
    """A dataclass to hold all application services for easy dependency injection."""
    cycle_service: ICycleService
    session_service: ISessionService
    exam_service: IExamService
    user_service: IUserService
    performance_service: IPerformanceService
    analytics_service: IAnalyticsService
    master_subject_service: IMasterSubjectService
    cycle_subject_service: ICycleSubjectService
    study_queue_service: IStudyQueueService
    work_unit_service: IWorkUnitService
    template_subject_service: ITemplateSubjectService