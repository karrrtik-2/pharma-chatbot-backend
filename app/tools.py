from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Literal

import pandas as pd
from langchain_core.tools import tool

from .models import DateModel, DateTimeModel, IdentificationNumberModel

DOCTOR_NAMES = Literal[
    "kevin anderson",
    "robert martinez",
    "susan davis",
    "daniel miller",
    "sarah wilson",
    "michael green",
    "lisa brown",
    "jane smith",
    "emily johnson",
    "john doe",
]

SPECIALIZATIONS = Literal[
    "general_dentist",
    "cosmetic_dentist",
    "prosthodontist",
    "pediatric_dentist",
    "emergency_dentist",
    "oral_surgeon",
    "orthodontist",
]

DATA_FILE = Path(__file__).resolve().parents[2] / "data" / "doctor_availability.csv"


def _load_schedule() -> pd.DataFrame:
    return pd.read_csv(DATA_FILE)


def _save_schedule(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)


@tool
def check_availability_by_doctor(desired_date: DateModel, doctor_name: DOCTOR_NAMES):
    """Checking the database if we have availability for the specific doctor."""
    df = _load_schedule()
    df["date_slot_time"] = df["date_slot"].apply(lambda value: value.split(" ")[-1])

    rows = list(
        df[
            (df["date_slot"].apply(lambda value: value.split(" ")[0]) == desired_date.date)
            & (df["doctor_name"] == doctor_name)
            & (df["is_available"] == True)
        ]["date_slot_time"]
    )

    if len(rows) == 0:
        return "No availability in the entire day"

    return f"This availability for {desired_date.date}\nAvailable slots: " + ", ".join(rows)


@tool
def check_availability_by_specialization(desired_date: DateModel, specialization: SPECIALIZATIONS):
    """Checking the database if we have availability for the specific specialization."""
    df = _load_schedule()
    df["date_slot_time"] = df["date_slot"].apply(lambda value: value.split(" ")[-1])
    rows = (
        df[
            (df["date_slot"].apply(lambda value: value.split(" ")[0]) == desired_date.date)
            & (df["specialization"] == specialization)
            & (df["is_available"] == True)
        ]
        .groupby(["specialization", "doctor_name"])["date_slot_time"]
        .apply(list)
        .reset_index(name="available_slots")
    )

    if len(rows) == 0:
        return "No availability in the entire day"

    def convert_to_am_pm(time_str: str) -> str:
        hours, minutes = map(int, str(time_str).split(":"))
        period = "AM" if hours < 12 else "PM"
        hours = hours % 12 or 12
        return f"{hours}:{minutes:02d} {period}"

    output = f"This availability for {desired_date.date}\n"
    for row in rows.values:
        output += row[1] + ". Available slots: \n" + ", \n".join([convert_to_am_pm(value) for value in row[2]]) + "\n"

    return output


@tool
def set_appointment(desired_date: DateTimeModel, id_number: IdentificationNumberModel, doctor_name: DOCTOR_NAMES):
    """Set appointment or slot with the doctor."""
    df = _load_schedule()

    def convert_datetime_format(date_time_str: str) -> str:
        dt = datetime.strptime(date_time_str, "%d-%m-%Y %H:%M")
        return dt.strftime("%d-%m-%Y %#H.%M")

    target = convert_datetime_format(desired_date.date)
    case = df[(df["date_slot"] == target) & (df["doctor_name"] == doctor_name) & (df["is_available"] == True)]

    if len(case) == 0:
        return "No available appointments for that particular case"

    df.loc[
        (df["date_slot"] == target) & (df["doctor_name"] == doctor_name) & (df["is_available"] == True),
        ["is_available", "patient_to_attend"],
    ] = [False, id_number.id]
    _save_schedule(df)

    return "Succesfully done"


@tool
def cancel_appointment(date: DateTimeModel, id_number: IdentificationNumberModel, doctor_name: DOCTOR_NAMES):
    """Canceling an appointment."""
    df = _load_schedule()
    case_to_remove = df[
        (df["date_slot"] == date.date)
        & (df["patient_to_attend"] == id_number.id)
        & (df["doctor_name"] == doctor_name)
    ]

    if len(case_to_remove) == 0:
        return "You don´t have any appointment with that specifications"

    df.loc[
        (df["date_slot"] == date.date)
        & (df["patient_to_attend"] == id_number.id)
        & (df["doctor_name"] == doctor_name),
        ["is_available", "patient_to_attend"],
    ] = [True, None]
    _save_schedule(df)

    return "Successfully cancelled"


@tool
def reschedule_appointment(
    old_date: DateTimeModel,
    new_date: DateTimeModel,
    id_number: IdentificationNumberModel,
    doctor_name: DOCTOR_NAMES,
):
    """Rescheduling an appointment."""
    df = _load_schedule()
    available_for_desired_date = df[
        (df["date_slot"] == new_date.date) & (df["is_available"] == True) & (df["doctor_name"] == doctor_name)
    ]
    if len(available_for_desired_date) == 0:
        return "Not available slots in the desired period"

    cancel_appointment.invoke({"date": old_date, "id_number": id_number, "doctor_name": doctor_name})
    set_appointment.invoke({"desired_date": new_date, "id_number": id_number, "doctor_name": doctor_name})
    return "Successfully rescheduled for the desired time"
