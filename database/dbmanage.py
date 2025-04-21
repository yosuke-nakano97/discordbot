import logging
from datetime import datetime, timedelta, timezone

import discord
from sqlalchemy import not_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, joinedload, scoped_session, sessionmaker

from database.models import (
    Channel_D,
    Channel_Y,
    Domain,
    Group,
    Message,
    Twitter,
    User,
    VoiceStatus,
    engine,
    Category,
    Booking,
    Roles,
)

# ロガーの設定
logger = logging.getLogger(__name__)

Session = scoped_session(sessionmaker(bind=engine))


class Dbmanage:

    def reg_message(self, user_id, time, url, id, channel_id, channel_name, category):
        logger.info(
            "reg_message called with user_id: %s, time: %s, url: %s, id: %s, channel_id: %s, channel_name: %s",
            user_id,
            time,
            url,
            id,
            channel_id,
            channel_name,
        )
        session = Session()

        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user is None:
                user = User(id=user_id)
                session.add(user)
                session.commit()
                logger.info("New user added: %s", user_id)
            else:
                logger.info("User found: %s", user_id)

            category_db = (
                session.query(Category).filter(Category.id == category.id).first()
            )
            if category_db is None:
                category_db = Category(id=category.id, name=category.name)
                session.add(category_db)
                session.commit()
                logger.info("New category added: %s", category_db.name)

            channel = (
                session.query(Channel_D).filter(Channel_D.id == channel_id).first()
            )
            if channel is None:
                channel = Channel_D(
                    id=channel_id, name=channel_name, category=category_db
                )
                session.add(channel)
                session.commit()
                logger.info("New channel added: %s", channel_id)
            else:
                logger.info("Channel found: %s", channel_id)

            user.increment()
            channel.increment()
            message = Message(url=url, time=time, user=user, id=id, channel=channel)
            session.add_all([user, message, channel])
            session.commit()
            logger.info("Message registered: %s", id)

        except SQLAlchemyError as e:
            logger.error("Error registering message: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def reg_channel_y(self, channel, id):
        # print(type(id))
        # print(channel)
        session = Session()

        try:
            channel_y = (
                session.query(Channel_Y).filter(Channel_Y.id == channel.id).first()
            )
            if channel_y is None:
                channel_y = Channel_Y(
                    id=channel.id, name=channel.name, icon=channel.icon
                )
                session.add(channel_y)
                session.commit()
            else:
                channel_y.increment()
                session.add(channel_y)
                session.commit()
            self.change_status(id, "success")
        except SQLAlchemyError as e:
            session.rollback()
            print(e)
        finally:
            session.close()
            Session.remove()

    def change_status(self, id, status):
        logger.info("change_status called with id: %s, status: %s", id, status)
        session = Session()

        try:
            message = session.query(Message).filter(Message.id == id).first()
            if message:
                message.status = status
                session.commit()
                logger.info("Message status changed: %s to %s", id, status)
            else:
                logger.warning("Message not found: %s", id)
        except SQLAlchemyError as e:
            logger.error("Error changing message status: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_message(self):
        logger.info("read_message called")
        session = Session()

        try:
            messages = session.query(Message).all()
            logger.info("Messages read: %d", len(messages))
            return messages
        except SQLAlchemyError as e:
            logger.error("Error reading messages: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_messages_by_user(self, user_id):
        logger.info("read_message_by_id called")
        session = Session()

        try:
            messages = session.query(Message).filter(Message.user_id == user_id).all()
            logger.info("Messages read: %d", len(messages))
            return messages
        except SQLAlchemyError as e:
            logger.error("Error reading messages: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def reg_domain(self, url_domain):
        logger.info("reg_domain called with url_domain: %s", url_domain)
        session = Session()

        try:
            domain = session.query(Domain).filter(Domain.domain == url_domain).first()
            if domain is None:
                logger.info("New domain added: %s", url_domain)
                domain = Domain(domain=url_domain)
                session.add(domain)
                session.commit()
            else:
                logger.info("Domain found and incremented: %s", url_domain)
                domain.increment()
                session.add(domain)
                session.commit()
        except SQLAlchemyError as e:
            logger.error("Error registering domain: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def reg_twitter(self, id, twitter_id):
        logger.info(
            "reg_twitter called with message_id: %s, twitter_id: %s", id, twitter_id
        )
        session = Session()

        try:
            twitter = session.query(Twitter).filter(Twitter.id == twitter_id).first()
            if twitter is None:
                twitter = Twitter(id=twitter_id)
                session.add(twitter)
                session.commit()
            else:
                twitter.increment()
                session.add(twitter)
                session.commit()
        except SQLAlchemyError as e:
            logger.error("Error registering Twitter: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_channels(self):
        logger.info("read_channels called")
        session = Session()

        try:
            channels = session.query(Channel_D).all()
            logger.info("Channels read: %d", len(channels))
            return channels
        except SQLAlchemyError as e:
            logger.error("Error reading channels: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_groups(self):
        logger.info("read_groups called")
        session = Session()

        try:
            groups = session.query(Group).all()
            logger.info("Groups read: %d", len(groups))
            return groups
        except SQLAlchemyError as e:
            logger.error("Error reading groups: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_channels_y(self):
        logger.info("read_channels_y called")
        session = Session()

        try:
            channels = (
                session.query(Channel_Y).options(joinedload(Channel_Y.group)).all()
            )
            logger.info("Channels read: %d", len(channels))
            return channels
        except SQLAlchemyError as e:
            logger.error("Error reading channels: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def reg_group(self, channel_id, group_name):
        logger.info(
            "reg_group called with channel_id: %s, group_name: %s",
            channel_id,
            group_name,
        )
        session = Session()

        try:
            group = session.query(Group).filter(Group.name == group_name).first()
            if group is None:
                group = Group(name=group_name)
                session.add(group)
                session.commit()
            channel = (
                session.query(Channel_Y).filter(Channel_Y.id == channel_id).first()
            )
            channel.group = group
            group.increment()
            session.add_all([channel, group])
            session.commit()
        except SQLAlchemyError as e:
            logger.error("Error registering group: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_channels_by_group(self, group_name):
        logger.info("read_channels_by_group called with group_id: %s", group_name)
        session = Session()

        try:
            channels = (
                session.query(Channel_Y).filter(Channel_Y.groupname == group_name).all()
            )
            logger.info("Channels read: %d", len(channels))
            return channels
        except SQLAlchemyError as e:
            logger.error("Error reading channels: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_users(self):
        logger.info("read_users called")
        session = Session()

        try:
            users = session.query(User).all()
            logger.info("Users read: %d", len(users))
            return users
        except SQLAlchemyError as e:
            logger.error("Error reading users: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_domains(self):
        logger.info("read_domains called")
        session = Session()

        try:
            domains = session.query(Domain).all()
            logger.info("Domains read: %d", len(domains))
            return domains
        except SQLAlchemyError as e:
            logger.error("Error reading domains: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_twitter(self):
        logger.info("read_twitter called")
        session = Session()

        try:
            twitters = session.query(Twitter).all()
            logger.info("Twitters read: %d", len(twitters))
            return twitters
        except SQLAlchemyError as e:
            logger.error("Error reading twitters: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def count_messages_this_year(self, channel_id):
        now = datetime.now()
        start_of_year = datetime(now.year, 1, 1)

        logger.info("count_messages_this_year called with channel_id: %s", channel_id)
        session = Session()

        try:
            count = (
                session.query(Message)
                .filter(Message.channel_id == channel_id, Message.time >= start_of_year)
                .count()
            )
            logger.info("Messages counted: %d", count)
            return count
        except SQLAlchemyError as e:
            logger.error("Error counting messages: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()
        logger.info("read_twitter called")
        session = Session()

        try:
            twitters = session.query().all()
            logger.info("Twitters read: %d", len(twitters))
            return twitters
        except SQLAlchemyError as e:
            logger.error("Error reading twitters: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def show_top_channel_in_group(self, writer):
        logger.info("show_top_channel_in_group called")
        session = Session()

        try:
            groups = session.query(Group).all()
            writer.writerow(["group", "channel", "count"])
            for group in groups:
                channels = (
                    session.query(Channel_Y)
                    .filter(Channel_Y.groupname == group.name)
                    .order_by(Channel_Y.count.desc())
                    .limit(5)
                    .all()
                )
                for channel in channels:
                    writer.writerow([group.name, channel.name, channel.count])
        except SQLAlchemyError as e:
            logger.error("Error showing top channel in group: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def reg_voice(self, member, channel, status):
        logger.info(
            "reg_voice called with channel_id: %s, user: %s",
            channel.id,
            member.id,
        )
        session = Session()

        try:
            time = datetime.now(timezone(timedelta(hours=9)))

            if status == "join":
                user = session.query(User).filter(User.id == member.name).first()
                if user is None:
                    user = User(id=member.name)
                    session.add(user)
                    session.commit()
                    logger.info("New user added: %s", member.id)
                channel_db = (
                    session.query(Channel_D).filter(Channel_D.id == channel.id).first()
                )
                if channel_db is None:
                    channel_db = Channel_D(id=channel.id, name=channel.name)
                    session.add(channel_db)
                    session.commit()
                    logger.info("New channel added: %s", channel.id)

                voice = VoiceStatus(user=user, channel=channel_db, start_at=time)
                session.add(voice)
                session.commit()

            if status == "exit":
                voice = (
                    session.query(VoiceStatus)
                    .filter(
                        VoiceStatus.user_id == member.name, VoiceStatus.end_at == None
                    )
                    .first()
                )
                voice.end_at = time
                session.add(voice)
                session.commit()

        except SQLAlchemyError as e:
            logger.error("Error registering group: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def reg_booking(self, booking):
        logger.info("reg_booking called")
        session = Session()
        new_booking = Booking(
            id=booking.id,
            user_id=booking.user_id,
            channel_id=booking.channel_id,
            datetime=booking.datetime,
            target=booking.target,
            role=booking.role,
            message=booking.message,
        )

        try:
            session.add(new_booking)
            session.commit()
            logger.info("Booking registered")
        except SQLAlchemyError as e:
            logger.error("Error registering booking: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def delete_booking(self, booking):
        logger.info("delete_booking called")
        session = Session()

        try:
            session.delete(booking)
            session.commit()
            logger.info("Booking deleted")
        except SQLAlchemyError as e:
            logger.error("Error deleting booking: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_booking_by_id(self, id):
        try:
            session = Session()
            booking = session.query(Booking).filter(Booking.id == id).first()
            session.close()
            Session.remove()
            return booking
        except SQLAlchemyError as e:
            logger.error("Error reading booking: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_booking_by_userid(self, user_id):
        try:
            session = Session()
            now = datetime.now(timezone(timedelta(hours=9)))
            booking = (
                session.query(Booking)
                .filter(Booking.user_id == user_id, Booking.datetime >= now)
                .all()
            )
            session.close()
            Session.remove()
            return booking
        except SQLAlchemyError as e:
            logger.error("Error reading booking: %s", e)
            session.rollback()
            return None
        finally:
            session.close()
            Session.remove()

    def update_booking(self, booking):
        logger.info("update_booking called")
        session = Session()

        try:
            current_booking = (
                session.query(Booking).filter(Booking.id == booking.id).first()
            )
            current_booking.target = booking.target
            current_booking.role = booking.role
            current_booking.message = booking.message
            current_booking.datetime = booking.datetime
            current_booking.channel_id = booking.channel_id
            current_booking.job_id = booking.job_id
            session.add(current_booking)
            session.commit()
            logger.info("Booking updated")
        except SQLAlchemyError as e:
            logger.error("Error updating booking: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def read_bookings(self):
        try:
            session = Session()
            bookings = session.query(Booking).filter().all()
            session.close()
            Session.remove()
            return bookings
        except SQLAlchemyError as e:
            logger.error("Error reading booking: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def get_all_voice(self):
        try:
            session = Session()
            voice = session.query(VoiceStatus).all()
            session.close()
            Session.remove()
            return voice
        except SQLAlchemyError as e:
            logger.error("Error reading voice: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def save_roles(self, roles):
        session = Session()
        try:
            session.query(Roles).delete()
            session.commit()
            for role in roles:
                new_role = Roles(id=role.id)
                session.add(new_role)
                session.commit()
            logger.info("Roles saved")
        except SQLAlchemyError as e:
            logger.error("Error saving roles: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()

    def load_roles(self):
        try:
            session = Session()
            roles = session.query(Roles).all()
            return roles
        except SQLAlchemyError as e:
            logger.error("Error loading roles: %s", e)
            session.rollback()
        finally:
            session.close()
            Session.remove()
