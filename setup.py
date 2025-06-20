from setuptools import setup, find_packages

setup(
    name="loreal_insight_agent",
    version="1.0.0",
    description="L'Oreal Sales Data Analysis and Visualization Agent",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        'gradio==5.29.1',
        'langchain==0.3.25',
        'langchain-community==0.3.24',
        'langchain-core==0.3.60',
        'matplotlib==3.10.3',
        'numpy==1.26.2',
        'openai==1.79.0',
        'pandas==2.2.3',
        'python-dotenv==1.1.0',
        'seaborn==0.13.2',
        'SQLAlchemy==2.0.41',
        'typer==0.15.4',
        'pydantic==2.11.4',
    ],
    python_requires='>=3.10,<3.11',
    classifiers=[
        'Programming Language :: Python :: 3.10',
    ],
)