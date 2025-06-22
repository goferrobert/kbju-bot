from contextlib import contextmanager
from typing import List, Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base, User, UserRecord, UserActivity, UserGoal, UserSettings, UserNotification

class Database:
    """Database connection and operations manager."""
    
    def __init__(self, db_url: str):
        """
        Initialize database connection.
        
        Args:
            db_url: Database connection URL
        """
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Get database session.
        
        Yields:
            Database session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_user(self, telegram_id: int) -> Optional[User]:
        """
        Get user by telegram ID.
        
        Args:
            telegram_id: User's Telegram ID
        
        Returns:
            User object or None if not found
        """
        with self.get_session() as session:
            return session.query(User).filter(User.telegram_id == telegram_id).first()
    
    def create_user(self, telegram_id: int, username: str, first_name: str, last_name: Optional[str] = None) -> User:
        """
        Create new user.
        
        Args:
            telegram_id: User's Telegram ID
            username: User's username
            first_name: User's first name
            last_name: User's last name (optional)
        
        Returns:
            Created User object
        
        Raises:
            SQLAlchemyError: If user creation fails
        """
        with self.get_session() as session:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name
            )
            session.add(user)
            session.flush()
            
            # Create default settings
            settings = UserSettings(user_id=user.id)
            session.add(settings)
            
            return user
    
    def update_user(self, telegram_id: int, **kwargs) -> Optional[User]:
        """
        Update user data.
        
        Args:
            telegram_id: User's Telegram ID
            **kwargs: User fields to update
        
        Returns:
            Updated User object or None if not found
        
        Raises:
            SQLAlchemyError: If update fails
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                for key, value in kwargs.items():
                    setattr(user, key, value)
                return user
            return None
    
    def get_user_records(self, telegram_id: int, limit: int = 30) -> List[UserRecord]:
        """
        Get user's records.
        
        Args:
            telegram_id: User's Telegram ID
            limit: Maximum number of records to return
        
        Returns:
            List of UserRecord objects
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                return session.query(UserRecord)\
                    .filter(UserRecord.user_id == user.id)\
                    .order_by(UserRecord.date.desc())\
                    .limit(limit)\
                    .all()
            return []
    
    def add_user_record(self, telegram_id: int, **kwargs) -> Optional[UserRecord]:
        """
        Add new user record.
        
        Args:
            telegram_id: User's Telegram ID
            **kwargs: Record fields
        
        Returns:
            Created UserRecord object or None if user not found
        
        Raises:
            SQLAlchemyError: If record creation fails
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                record = UserRecord(user_id=user.id, **kwargs)
                session.add(record)
                return record
            return None
    
    def get_user_goal(self, telegram_id: int) -> Optional[UserGoal]:
        """
        Get user's goal.
        
        Args:
            telegram_id: User's Telegram ID
        
        Returns:
            UserGoal object or None if not found
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                return session.query(UserGoal)\
                    .filter(UserGoal.user_id == user.id)\
                    .order_by(UserGoal.created_at.desc())\
                    .first()
            return None
    
    def set_user_goal(self, telegram_id: int, **kwargs) -> Optional[UserGoal]:
        """
        Set user's goal.
        
        Args:
            telegram_id: User's Telegram ID
            **kwargs: Goal fields
        
        Returns:
            Created UserGoal object or None if user not found
        
        Raises:
            SQLAlchemyError: If goal creation fails
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                goal = UserGoal(user_id=user.id, **kwargs)
                session.add(goal)
                return goal
            return None
    
    def get_user_settings(self, telegram_id: int) -> Optional[UserSettings]:
        """
        Get user's settings.
        
        Args:
            telegram_id: User's Telegram ID
        
        Returns:
            UserSettings object or None if not found
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                return session.query(UserSettings)\
                    .filter(UserSettings.user_id == user.id)\
                    .first()
            return None
    
    def update_user_settings(self, telegram_id: int, **kwargs) -> Optional[UserSettings]:
        """
        Update user's settings.
        
        Args:
            telegram_id: User's Telegram ID
            **kwargs: Settings fields to update
        
        Returns:
            Updated UserSettings object or None if not found
        
        Raises:
            SQLAlchemyError: If update fails
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                settings = session.query(UserSettings)\
                    .filter(UserSettings.user_id == user.id)\
                    .first()
                if settings:
                    for key, value in kwargs.items():
                        setattr(settings, key, value)
                    return settings
            return None
    
    def get_user_notifications(self, telegram_id: int) -> List[UserNotification]:
        """
        Get user's notifications.
        
        Args:
            telegram_id: User's Telegram ID
        
        Returns:
            List of UserNotification objects
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                return session.query(UserNotification)\
                    .filter(UserNotification.user_id == user.id)\
                    .order_by(UserNotification.time)\
                    .all()
            return []
    
    def add_user_notification(self, telegram_id: int, **kwargs) -> Optional[UserNotification]:
        """
        Add new user notification.
        
        Args:
            telegram_id: User's Telegram ID
            **kwargs: Notification fields
        
        Returns:
            Created UserNotification object or None if user not found
        
        Raises:
            SQLAlchemyError: If notification creation fails
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                notification = UserNotification(user_id=user.id, **kwargs)
                session.add(notification)
                return notification
            return None
    
    def update_user_notification(self, notification_id: int, **kwargs) -> Optional[UserNotification]:
        """
        Update user notification.
        
        Args:
            notification_id: Notification ID
            **kwargs: Notification fields to update
        
        Returns:
            Updated UserNotification object or None if not found
        
        Raises:
            SQLAlchemyError: If update fails
        """
        with self.get_session() as session:
            notification = session.query(UserNotification)\
                .filter(UserNotification.id == notification_id)\
                .first()
            if notification:
                for key, value in kwargs.items():
                    setattr(notification, key, value)
                return notification
            return None
    
    def delete_user_notification(self, notification_id: int) -> bool:
        """
        Delete user notification.
        
        Args:
            notification_id: Notification ID
        
        Returns:
            True if deleted, False if not found
        
        Raises:
            SQLAlchemyError: If deletion fails
        """
        with self.get_session() as session:
            notification = session.query(UserNotification)\
                .filter(UserNotification.id == notification_id)\
                .first()
            if notification:
                session.delete(notification)
                return True
            return False
    
    def get_active_notifications(self) -> List[UserNotification]:
        """
        Get all active notifications.
        
        Returns:
            List of active UserNotification objects
        """
        with self.get_session() as session:
            return session.query(UserNotification)\
                .filter(UserNotification.is_active.is_(True))\
                .order_by(UserNotification.time)\
                .all()
    
    def get_user_activities(self, telegram_id: int, limit: int = 30) -> List[UserActivity]:
        """
        Get user's activities.
        
        Args:
            telegram_id: User's Telegram ID
            limit: Maximum number of activities to return
        
        Returns:
            List of UserActivity objects
        """
        with self.get_session() as session:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                return session.query(UserActivity)\
                    .join(UserRecord)\
                    .filter(UserRecord.user_id == user.id)\
                    .order_by(UserActivity.created_at.desc())\
                    .limit(limit)\
                    .all()
            return []
    
    def add_user_activity(self, record_id: int, **kwargs) -> Optional[UserActivity]:
        """
        Add new user activity.
        
        Args:
            record_id: Record ID
            **kwargs: Activity fields
        
        Returns:
            Created UserActivity object or None if record not found
        
        Raises:
            SQLAlchemyError: If activity creation fails
        """
        with self.get_session() as session:
            record = session.query(UserRecord).filter(UserRecord.id == record_id).first()
            if record:
                activity = UserActivity(record_id=record_id, **kwargs)
                session.add(activity)
                return activity
            return None 