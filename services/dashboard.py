def view_patient_dashboard(patient, dashboard):
    print("\n📊 Medora Dashboard:")
    summary = dashboard.generate_summary(patient)
    for k, v in summary.items():
        print(f"- {k}: {v}")
    print()

def view_doctor_dashboard(doctor):
    print("\n📊 Medora Dashboard:")
    print(f"Doctor ID: {doctor.user_id}")
    print(f"Name: {doctor.name}")
    print(f"Specialization: {doctor.specialization}")
    print(f"Connected Patients: {len(doctor.patients)}")
    if doctor.patients:
        print("Patients:")
        for p in doctor.patients:
            print(f"  - {p.name} ({p.email})")
    else:
        print("No patients connected yet.")
    print()
