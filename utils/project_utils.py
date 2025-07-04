import os
import datetime
from typing import Optional


def create_project(proj_dir: str, add_name: Optional[str] = None) -> dict[str, str]:
    """
    Prepare folder for concrete project.

    :param proj_dir: path to folder for ALL projects
    :param add_name: additional name of project (e.g. Brand Manager name)
    :return: a dictionary with project folders paths
    """
    now = datetime.datetime.now()
    now_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    # Можно добавить миллисекунды для большей уникальности:
    # folder_name = now.strftime("%Y-%m-%d_%H-%M-%S-%f")

    project_name = f"{now_string}_{add_name}" if add_name else now_string

    this_proj_dir = os.path.join(proj_dir, project_name)
    if not os.path.exists(this_proj_dir):
        os.mkdir(this_proj_dir)

    graphs_dir = os.path.join(this_proj_dir, "graphs")
    if not os.path.exists(graphs_dir):
        os.mkdir(graphs_dir)

    labels_dir = os.path.join(this_proj_dir, "labels")
    if not os.path.exists(labels_dir):
        os.mkdir(labels_dir)

    project_data = {
        "project_name": project_name,
        "project_folder": this_proj_dir,
        "graphs": graphs_dir,
        "labels": labels_dir
    }
    return project_data


def remove_project(project_path: str) -> None:
    """Delete temporary files in selected folder"""
    for filename in os.listdir(project_path):
        file_path = os.path.join(project_path, filename)
        os.remove(file_path)