import json
import os
import uuid

EVENTS_FILE = 'events.json'
WORKERS_FILE = 'workers.json'

class Worker:
    def __init__(self, name, role, pay_rate, worker_id=None, assigned_event_ids=None):
        self.worker_id = worker_id or str(uuid.uuid4())[:8]
        self.name = name
        self.role = role
        self.pay_rate = pay_rate
        self.assigned_event_ids = assigned_event_ids or []

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        return Worker(
            data['name'],
            data['role'],
            data['pay_rate'],
            data['worker_id'],
            data['assigned_event_ids']
        )

    def __str__(self):
        return f"Worker: {self.name} (ID: {self.worker_id}) | Role: {self.role} | Rate: ${self.pay_rate}/hr"

class Event:
    def __init__(self, name, date, location, event_id=None, assigned_workers=None):
        self.event_id = event_id or str(uuid.uuid4())[:8]
        self.name = name
        self.date = date
        self.location = location
        self.assigned_workers = assigned_workers or {} # {worker_id: hours}

    def to_dict(self):
        return self.__dict__
    
    @staticmethod
    def from_dict(data):
        return Event(
            data['name'],
            data['date'],
            data['location'],
            data['event_id'],
            data['assigned_workers']
        )

    def __str__(self):
        return f"Event: {self.name} (ID: {self.event_id}) | Date: {self.date} | Location: {self.location}"

class LaborManagementSystem:
    def __init__(self):
        self.events = {}
        self.workers = {}
        self.load_data()

    def load_data(self):
        try:
            if os.path.exists(EVENTS_FILE):
                with open(EVENTS_FILE, 'r') as f:
                    events_data = json.load(f)
                    for event_id, data in events_data.items():
                        self.events[event_id] = Event.from_dict(data)
            if os.path.exists(WORKERS_FILE):
                with open(WORKERS_FILE, 'r') as f:
                    workers_data = json.load(f)
                    for worker_id, data in workers_data.items():
                        self.workers[worker_id] = Worker.from_dict(data)
            print("Data loaded successfully.")
        except json.JSONDecodeError:
            print("Warning: Could not decode data files. Starting with empty data.")
        except Exception as e:
            print(f"Error loading data: {e}")

    def save_data(self):
        try:
            with open(EVENTS_FILE, 'w') as f:
                json.dump({eid: event.to_dict() for eid, event in self.events.items()}, f, indent=4)
            with open(WORKERS_FILE, 'w') as f:
                json.dump({wid: worker.to_dict() for wid, worker in self.workers.items()}, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    def add_event(self):
        print("\n--- Add New Event ---")
        name = input("Enter event name: ")
        date = input("Enter event date (YYYY-MM-DD): ")
        location = input("Enter event location: ")
        event = Event(name, date, location)
        self.events[event.event_id] = event
        self.save_data()
        print(f"Success: Added event '{name}' with ID {event.event_id}")

    def add_worker(self):
        print("\n--- Add New Worker ---")
        name = input("Enter worker's name: ")
        role = input("Enter worker's role (e.g., Security, Catering, Tech): ")
        try:
            pay_rate = float(input("Enter worker's hourly pay rate: "))
            worker = Worker(name, role, pay_rate)
            self.workers[worker.worker_id] = worker
            self.save_data()
            print(f"Success: Added worker '{name}' with ID {worker.worker_id}")
        except ValueError:
            print("Error: Invalid pay rate. Please enter a number.")

    def list_events(self, show_details=False):
        print("\n--- All Events ---")
        if not self.events:
            print("No events found.")
            return False
        
        for event_id, event in self.events.items():
            print(event)
            if show_details:
                print("  Assigned Workers:")
                if not event.assigned_workers:
                    print("    - None")
                else:
                    for worker_id, hours in event.assigned_workers.items():
                        worker = self.workers.get(worker_id)
                        if worker:
                            print(f"    - {worker.name} ({worker.role}) for {hours} hours")
                        else:
                            print(f"    - Error: Worker ID {worker_id} not found")
                print("-" * 20)
        return True

    def list_workers(self):
        print("\n--- All Workers ---")
        if not self.workers:
            print("No workers found.")
            return False
        
        for worker_id, worker in self.workers.items():
            print(worker)
        return True

    def assign_worker_to_event(self):
        print("\n--- Assign Worker to Event ---")
        if not self.list_events():
            return
        try:
            event_id = input("Enter the Event ID to assign a worker to: ")
            event = self.events.get(event_id)
            if not event:
                print("Error: Event not found.")
                return

            if not self.list_workers():
                return
            worker_id = input("Enter the Worker ID to assign: ")
            worker = self.workers.get(worker_id)
            if not worker:
                print("Error: Worker not found.")
                return
            
            if worker_id in event.assigned_workers:
                print(f"Info: Worker {worker.name} is already assigned to {event.name}.")
                return

            hours = float(input(f"Enter estimated hours for {worker.name}: "))
            
            event.assigned_workers[worker_id] = hours
            worker.assigned_event_ids.append(event_id)
            self.save_data()
            print(f"Success: Assigned {worker.name} to {event.name} for {hours} hours.")

        except ValueError:
            print("Error: Invalid ID or hours. Please enter correctly.")

    def remove_worker_from_event(self):
        print("\n--- Remove Worker from Event ---")
        if not self.list_events():
            return
        try:
            event_id = input("Enter the Event ID: ")
            event = self.events.get(event_id)
            if not event:
                print("Error: Event not found.")
                return
            
            if not event.assigned_workers:
                print(f"No workers assigned to {event.name}.")
                return

            print(f"Workers assigned to {event.name}:")
            for worker_id in event.assigned_workers:
                worker = self.workers.get(worker_id)
                print(f"  - {worker.name} (ID: {worker_id})")
            
            worker_id = input("Enter the Worker ID to remove: ")
            if worker_id not in event.assigned_workers:
                print("Error: This worker is not assigned to this event.")
                return

            worker = self.workers.get(worker_id)
            del event.assigned_workers[worker_id]
            
            if worker and event_id in worker.assigned_event_ids:
                worker.assigned_event_ids.remove(event_id)
            
            self.save_data()
            print(f"Success: Removed {worker.name} from {event.name}.")

        except ValueError:
            print("Error: Invalid ID. Please enter correctly.")
            
    def delete_event(self):
        print("\n--- Delete Event ---")
        if not self.list_events():
            return
        try:
            event_id = input("Enter the Event ID to DELETE: ")
            event = self.events.get(event_id)
            if not event:
                print("Error: Event not found.")
                return
            
            confirm = input(f"Are you sure you want to delete '{event.name}'? This cannot be undone. (yes/no): ").lower()
            if confirm == 'yes':
                del self.events[event_id]
                for worker in self.workers.values():
                    if event_id in worker.assigned_event_ids:
                        worker.assigned_event_ids.remove(event_id)
                self.save_data()
                print(f"Success: Event '{event.name}' has been deleted.")
            else:
                print("Deletion cancelled.")
        except ValueError:
            print("Error: Invalid ID.")
            
    def delete_worker(self):
        print("\n--- Delete Worker ---")
        if not self.list_workers():
            return
        try:
            worker_id = input("Enter the Worker ID to DELETE: ")
            worker = self.workers.get(worker_id)
            if not worker:
                print("Error: Worker not found.")
                return
            
            confirm = input(f"Are you sure you want to delete '{worker.name}'? This cannot be undone. (yes/no): ").lower()
            if confirm == 'yes':
                del self.workers[worker_id]
                for event in self.events.values():
                    if worker_id in event.assigned_workers:
                        del event.assigned_workers[worker_id]
                self.save_data()
                print(f"Success: Worker '{worker.name}' has been deleted.")
            else:
                print("Deletion cancelled.")
        except ValueError:
            print("Error: Invalid ID.")

    def calculate_event_cost(self):
        print("\n--- Calculate Event Labor Cost ---")
        if not self.list_events():
            return
        try:
            event_id = input("Enter the Event ID to calculate costs for: ")
            event = self.events.get(event_id)
            if not event:
                print("Error: Event not found.")
                return
            
            if not event.assigned_workers:
                print(f"No workers assigned to {event.name}. Total cost: $0.00")
                return
            
            total_cost = 0
            print(f"\nCost calculation for {event.name}:")
            for worker_id, hours in event.assigned_workers.items():
                worker = self.workers.get(worker_id)
                if worker:
                    cost = worker.pay_rate * hours
                    print(f"  - {worker.name} ({worker.role}): ${worker.pay_rate}/hr * {hours} hours = ${cost:.2f}")
                    total_cost += cost
                else:
                    print(f"  - Error: Worker ID {worker_id} not found. Cannot calculate cost.")
            
            print("-" * 20)
            print(f"Total Estimated Labor Cost: ${total_cost:.2f}")

        except ValueError:
            print("Error: Invalid ID.")

    def view_event_details(self):
        print("\n--- View Event Details ---")
        self.list_events(show_details=True)

    def run(self):
        print("Welcome to the Event Labor Management System")
        while True:
            print("\n" + "=" * 20)
            print("--- Main Menu ---")
            print("=" * 20)
            print("1. Add Event")
            print("2. Add Worker")
            print("3. Assign Worker to Event")
            print("4. Remove Worker from Event")
            print("5. View Event Details (with Workers)")
            print("6. View All Workers")
            print("7. Calculate Event Labor Cost")
            print("8. Delete Event")
            print("9. Delete Worker")
            print("10. Exit")
            
            choice = input("Enter your choice (1-10): ")
            
            if choice == '1':
                self.add_event()
            elif choice == '2':
                self.add_worker()
            elif choice == '3':
                self.assign_worker_to_event()
            elif choice == '4':
                self.remove_worker_from_event()
            elif choice == '5':
                self.view_event_details()
            elif choice == '6':
                self.list_workers()
            elif choice == '7':
                self.calculate_event_cost()
            elif choice == '8':
                self.delete_event()
            elif choice == '9':
                self.delete_worker()
            elif choice == '10':
                print("Exiting system. Goodbye!")
                break
            else:
                print("Invalid choice. Please enter a number between 1 and 10.")

if __name__ == "__main__":
    system = LaborManagementSystem()
    system.run()