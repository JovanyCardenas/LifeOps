# Suggested GitHub Issues

Copy these into GitHub issues after publishing the repo.

## Foundation

### Add user registration
Build a registration page using Django forms. New users should get a profile automatically and land on an empty dashboard.

Acceptance criteria:
- Users can create an account.
- Duplicate usernames show a helpful error.
- New users cannot see demo data.
- Tests cover registration success and validation errors.

### Add profile editing
Let users edit display name, role, and basic profile information.

Acceptance criteria:
- Authenticated users can update their own profile.
- Users cannot edit another user's profile.
- Tests cover ownership.

### Add production settings
Prepare the app for deployment.

Acceptance criteria:
- Secret key and allowed hosts are environment-driven.
- Debug can be disabled from environment variables.
- Static files work in production.
- README includes deployment notes.

## Planning

### Build requirement CRUD
Add list, create, edit, complete, and delete flows for requirements.

Acceptance criteria:
- Requirements are scoped to the current user.
- Users can filter by assignments, bills, tasks, and completion status.
- Tests cover create, update, delete, and privacy.

### Build schedule CRUD
Add calendar-style event management for work, school, and personal schedules.

Acceptance criteria:
- Users can create, edit, and delete events.
- Events can be filtered by category.
- Invalid end times are rejected.
- Tests cover validation and privacy.

## Finance

### Build budget management
Add CRUD for monthly budget categories and visual progress.

Acceptance criteria:
- Users can add spending and monthly limits.
- Dashboard shows remaining budget.
- Over-budget categories are clearly marked.
- Tests cover calculations.

### Build debt payoff tracker
Track balances, APR, minimum payments, and payoff progress.

Acceptance criteria:
- Users can add and update debts.
- Dashboard summarizes total debt.
- Tests cover calculations and ownership.

## Wellness

### Build habit check-ins
Let users check off habits and maintain streaks.

Acceptance criteria:
- Users can create habits.
- Users can record daily check-ins.
- Streaks update predictably.
- Tests cover streak behavior.

### Build gym progress tracker
Add workout templates, exercise logs, and progress history.

Acceptance criteria:
- Users can log workouts and exercises.
- Users can view recent workout history.
- Tests cover private workout data.

## Meals

### Build recipe library
Add recipes with ingredients, instructions, and nutrition notes.

Acceptance criteria:
- Users can create recipes.
- Recipes can be attached to meal plans.
- Tests cover ownership.

### Generate grocery list from meal plan
Create a grocery list from upcoming planned meals.

Acceptance criteria:
- Users can select a date range.
- Ingredients are grouped and summed where possible.
- Tests cover generated list output.

## Career

### Build job application pipeline
Add board-style columns for saved, applied, interviewing, offer, and rejected jobs.

Acceptance criteria:
- Users can move applications between statuses.
- Users can track deadlines and notes.
- Tests cover status updates.

## Collaboration

### Add message compose flow
Let users send messages to other users.

Acceptance criteria:
- Authenticated users can send messages.
- Users can see sent and received messages.
- Users cannot see unrelated messages.
- Tests cover message privacy.

### Add shared groups
Create households, classes, or teams for shared schedules and tasks.

Acceptance criteria:
- Users can create a group.
- Group owners can invite users.
- Shared records are visible only to group members.
- Tests cover group permissions.
