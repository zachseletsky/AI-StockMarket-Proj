# Use the official Conda base image
FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy environment file first for caching
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml

# Activate the environment by default in all shells
RUN echo "conda activate ai-stock-trader" >> ~/.bashrc

# Copy the rest of your app
COPY . .

# Use bash with conda activated
SHELL ["bash", "-c"]

# Optional: expose port if using API or Jupyter
# EXPOSE 8888

# Default command (edit as needed)
CMD ["conda", "run", "-n", "ai-stock-trader", "python", "app/main.py"]
