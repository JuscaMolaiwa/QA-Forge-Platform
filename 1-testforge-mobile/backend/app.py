from flask import Flask
from config import Config
from extensions import db, socketio, cors
from routes import devices_bp, tests_bp, reports_bp, library_bp
from routes.library import seed_from_disk
from services import DeviceManager, TestExecutor, QueueManager


def create_app(config: Config = None) -> Flask:
    app = Flask(__name__)
    cfg = config or Config()
    app.config.from_object(cfg)

    db.init_app(app)
    socketio.init_app(
        app,
        cors_allowed_origins=cfg.CORS_ORIGINS + [cfg.CORS_ORIGINS_REGEX],
        async_mode="threading",
        logger=False,
        engineio_logger=False,
    )
    cors.init_app(app, origins=cfg.CORS_ORIGINS, supports_credentials=True)

    app.register_blueprint(devices_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(library_bp)

    @app.get("/api/health")
    def health():
        return {"status": "ok", "queue_depth": app.queue_manager.depth()}

    app.queue_manager = QueueManager(max_size=cfg.MAX_QUEUE_SIZE)
    app.device_manager = DeviceManager(cfg)
    app.test_executor = TestExecutor(cfg, app.device_manager, app.queue_manager)

    with app.app_context():
        db.create_all()
        seed_from_disk()

    app.test_executor.start(app)

    return app


app = create_app()

if __name__ == "__main__":
    cfg = Config()
    socketio.run(app, host=cfg.HOST, port=cfg.PORT, debug=False)