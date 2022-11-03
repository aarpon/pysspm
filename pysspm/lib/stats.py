from pathlib import Path
from typing import Optional, Union

import pandas as pd

__doc__ = "Internal classes and functions to collect project statistics."

from .project import ProjectManager


class StatisticManager:
    """Class Stats that takes care of collecting project statistics."""

    @staticmethod
    def get_stats(projects_folder: Union[Path, str]) -> Union[None, pd.DataFrame]:
        """Return statistics for all projects, sorted by year and group.

        Parameters
        ----------

        projects_folder: Path
            Path to the root of the projects folder.

        Returns
        -------

        stats: Union[None|pd.Dataframe]
            Dataframe containing project statistics or None if compilation was not successful.
        """

        # Retrieve the projects table
        project_dataframe = ProjectManager.get_projects(projects_folder, detailed=True)

        # If nothing found, return
        if project_dataframe is None:
            return None

        # Group them by year and group
        statistics_dataframe = (
            project_dataframe.groupby(["Year", "Group"])
            .size()
            .reset_index(name="Projects")
        ).sort_values(by="Year", ascending=False)

        # Return
        return statistics_dataframe
