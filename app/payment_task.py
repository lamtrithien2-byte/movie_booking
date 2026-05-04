from app.celery_app import celery_app
from app.db.db_database import SessionLocal
from app.repositories import repo_payment
from app.services import service_payment


def run_with_db(task, action):
    db = SessionLocal()
    try:
        action(db)
    except Exception as exc:
        db.rollback()
        raise task.retry(exc=exc, countdown=10) from exc
    finally:
        db.close()


@celery_app.task(name="check_payment_status", bind=True, max_retries=3)
def check_payment_status(self, payment_id: int):
    def action(db):
        payment = repo_payment.get_payment_by_id(db, payment_id)
        if payment is None:
            return
        service_payment.sync_payos_payment(db, payment)

    run_with_db(self, action)


@celery_app.task(name="check_payment_by_order_code", bind=True, max_retries=3)
def check_payment_by_order_code(self, order_code: int):
    def action(db):
        payment = repo_payment.get_payment_by_order_code(db, order_code)
        if payment is None:
            return
        service_payment.sync_payos_payment(db, payment)

    run_with_db(self, action)


@celery_app.task(name="scan_pending_payments")
def scan_pending_payments():
    db = SessionLocal()
    try:
        payments = repo_payment.get_pending_payments(db).all()
        for payment in payments:
            check_payment_status.delay(payment.id)
    finally:
        db.close()
