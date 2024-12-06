from flask import Flask, render_template, request, redirect, url_for, session
import random

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Initialize global data
allocation_details = {}
previous_allocations = set()


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # Reset global data for new setup
        global allocation_details, previous_allocations
        allocation_details = {}
        previous_allocations = set()

        # Read input for allocation details
        fields = int(request.form["fields"])
        for i in range(1, fields + 1):
            field_name = request.form[f"field_name_{i}"]
            min_mark = int(request.form[f"min_mark_{i}"])
            max_mark = int(request.form[f"max_mark_{i}"])
            allocation_details[field_name] = (min_mark, max_mark)
        
        # Redirect to the allocation page
        return redirect(url_for("allocate"))
    
    return render_template("index.html")


@app.route("/allocate", methods=["GET", "POST"])
def allocate():
    global allocation_details, previous_allocations

    if request.method == "POST":
        total_marks = int(request.form["total_marks"])

        # Exit condition
        if total_marks == 5599:
            return render_template("allocate.html", exit=True)
        
        # Validation
        min_total = sum(details[0] for details in allocation_details.values())
        max_total = sum(details[1] for details in allocation_details.values())

        if total_marks < min_total or total_marks > max_total:
            return render_template("allocate.html", error="Total marks cannot be distributed with the given constraints.")

        # Generate unique allocation
        while True:
            marks = {field_name: details[0] for field_name, details in allocation_details.items()}
            remaining_marks = total_marks - sum(marks.values())
            
            fields_list = list(allocation_details.keys())
            while remaining_marks > 0:
                field_name = random.choice(fields_list)
                current_mark = marks[field_name]
                max_allowed = allocation_details[field_name][1]
                if current_mark < max_allowed:
                    increment = min(remaining_marks, max_allowed - current_mark)
                    marks[field_name] += increment
                    remaining_marks -= increment

            # Check for unique allocation
            allocation_tuple = tuple(marks.values())
            if allocation_tuple not in previous_allocations:
                previous_allocations.add(allocation_tuple)
                break
        
        # Return allocation results
        return render_template(
            "allocate.html",
            marks=marks,
            total_marks=total_marks,
            error=None,
            exit=False
        )
    
    return render_template("allocate.html", error=None, exit=False)


if __name__ == "__main__":
    app.run(debug=True)
