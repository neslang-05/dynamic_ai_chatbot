from setuptools import setup, find_packages

setup(
    name="dynamic_ai_chatbot",
    version="1.0.0",
    description="Intelligent, multi-platform AI chatbot with self-learning capabilities",
    author="Dynamic AI Team",
    packages=find_packages(),
    install_requires=[
        "transformers>=4.35.0",
        "torch>=2.1.0",
        "nltk>=3.8.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.0",
        "sentence-transformers>=2.2.0",
        "fastapi>=0.104.0",
        "uvicorn>=0.24.0",
        "sqlalchemy>=2.0.0",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "chatbot-cli=chatbot.cli:main",
            "chatbot-server=chatbot.server:main",
        ],
    },
)