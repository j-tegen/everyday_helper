from project.server import app, config
import os

if __name__ == "__main__":
	port = int(os.environ.get('‌​PORT', 5000))
	app.run(host=config.host_ip, port=port,debug=False)