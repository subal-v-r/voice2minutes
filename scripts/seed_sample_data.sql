-- Seed database with sample meeting data for testing

-- Clear existing data
DELETE FROM action_history;
DELETE FROM participants;
DELETE FROM actions;
DELETE FROM meetings;

-- Reset auto-increment counters
DELETE FROM sqlite_sequence WHERE name IN ('meetings', 'actions', 'participants', 'action_history');

-- Insert sample meetings
INSERT INTO meetings (filename, title, participants, summary, duration, agenda_items, decisions, risks, next_steps) VALUES
(
    'team_standup_2024_01_15.mp3',
    'Weekly Team Standup - January 15, 2024',
    'John Doe,Jane Smith,Bob Johnson,Alice Brown',
    'Weekly standup covering sprint progress, blockers, and upcoming deliverables. Team discussed current sprint velocity and identified potential risks.',
    1800,
    '["Sprint Progress Review", "Blocker Discussion", "Next Week Planning", "Risk Assessment"]',
    '["Extend current sprint by 2 days", "Prioritize bug fixes over new features", "Schedule additional code review sessions"]',
    '["Potential delay in API integration", "Resource constraints for testing", "Dependency on external vendor"]',
    '["Complete user authentication module", "Conduct performance testing", "Update project documentation"]'
),
(
    'product_planning_2024_01_12.mp3',
    'Q1 Product Planning Session',
    'Alice Brown,Charlie Wilson,David Lee,Emma Davis',
    'Comprehensive planning session for Q1 product roadmap. Discussed feature priorities, resource allocation, and market requirements.',
    3600,
    '["Q1 Feature Roadmap", "Resource Planning", "Market Analysis", "Technical Architecture Review"]',
    '["Focus on mobile app improvements", "Allocate 40% resources to performance optimization", "Implement new analytics dashboard"]',
    '["Competitive pressure from new market entrants", "Technical debt in legacy systems", "Potential skill gaps in team"]',
    '["Finalize feature specifications", "Conduct user research sessions", "Set up development environments"]'
),
(
    'client_review_2024_01_10.mp3',
    'Client Project Review Meeting',
    'Sarah Connor,Mike Ross,Lisa Wang',
    'Monthly review with client covering project milestones, deliverables, and feedback. Discussed scope changes and timeline adjustments.',
    2700,
    '["Milestone Review", "Client Feedback Discussion", "Scope Changes", "Timeline Adjustment"]',
    '["Approve additional budget for scope expansion", "Extend project timeline by 3 weeks", "Add two additional team members"]',
    '["Scope creep affecting original timeline", "Budget constraints for additional features", "Client expectations vs technical feasibility"]',
    '["Prepare revised project proposal", "Schedule technical feasibility assessment", "Update project timeline and milestones"]'
);

-- Insert sample participants with speaking time
INSERT INTO participants (meeting_id, speaker_name, speaking_time) VALUES
-- Team Standup participants
(1, 'John Doe', 420.5),
(1, 'Jane Smith', 380.2),
(1, 'Bob Johnson', 290.8),
(1, 'Alice Brown', 315.1),

-- Product Planning participants
(2, 'Alice Brown', 890.3),
(2, 'Charlie Wilson', 720.6),
(2, 'David Lee', 650.4),
(2, 'Emma Davis', 580.2),

-- Client Review participants
(3, 'Sarah Connor', 980.7),
(3, 'Mike Ross', 720.3),
(3, 'Lisa Wang', 650.9);

-- Insert sample actions
INSERT INTO actions (meeting_file, meeting_id, action_text, assignees, deadline, deadline_urgency, status, confidence, speaker, start_time, end_time) VALUES
-- Actions from Team Standup
('team_standup_2024_01_15.mp3', 1, 'John will send the updated project timeline by Friday', 'John Doe', '2024-01-19T17:00:00', 'medium', 'open', 0.85, 'Jane Smith', 420.5, 435.2),
('team_standup_2024_01_15.mp3', 1, 'Jane needs to review the code changes before deployment', 'Jane Smith', '2024-01-18T12:00:00', 'high', 'open', 0.92, 'John Doe', 680.3, 695.8),
('team_standup_2024_01_15.mp3', 1, 'Bob should update the test cases for the new API endpoints', 'Bob Johnson', '2024-01-20T17:00:00', 'medium', 'open', 0.78, 'Alice Brown', 1120.1, 1135.6),
('team_standup_2024_01_15.mp3', 1, 'Alice will coordinate with the QA team for integration testing', 'Alice Brown', '2024-01-22T10:00:00', 'low', 'open', 0.81, 'Bob Johnson', 1450.2, 1468.9),

-- Actions from Product Planning
('product_planning_2024_01_12.mp3', 2, 'Alice will prepare the feature specifications document by next week', 'Alice Brown', '2024-01-19T17:00:00', 'high', 'open', 0.88, 'Charlie Wilson', 1200.5, 1218.3),
('product_planning_2024_01_12.mp3', 2, 'Charlie needs to conduct user research sessions for the new dashboard', 'Charlie Wilson', '2024-01-25T17:00:00', 'medium', 'open', 0.76, 'David Lee', 1800.2, 1820.7),
('product_planning_2024_01_12.mp3', 2, 'David will set up the development environment for mobile testing', 'David Lee', '2024-01-17T12:00:00', 'urgent', 'open', 0.91, 'Emma Davis', 2400.8, 2415.4),
('product_planning_2024_01_12.mp3', 2, 'Emma should analyze competitor features and prepare comparison report', 'Emma Davis', '2024-01-30T17:00:00', 'low', 'open', 0.73, 'Alice Brown', 3000.1, 3018.6),

-- Actions from Client Review
('client_review_2024_01_10.mp3', 3, 'Sarah will prepare the revised project proposal with new scope', 'Sarah Connor', '2024-01-15T17:00:00', 'urgent', 'completed', 0.94, 'Mike Ross', 1500.3, 1520.8),
('client_review_2024_01_10.mp3', 3, 'Mike needs to schedule technical feasibility assessment meeting', 'Mike Ross', '2024-01-18T10:00:00', 'high', 'open', 0.87, 'Lisa Wang', 2100.5, 2118.2),
('client_review_2024_01_10.mp3', 3, 'Lisa will update project timeline and communicate to stakeholders', 'Lisa Wang', '2024-01-20T17:00:00', 'medium', 'open', 0.82, 'Sarah Connor', 2500.7, 2520.1);

-- Insert sample action history
INSERT INTO action_history (action_id, old_status, new_status, changed_by, change_reason) VALUES
(9, 'open', 'completed', 'Sarah Connor', 'Proposal completed and submitted to client'),
(9, 'completed', 'completed', 'System', 'Automatically marked as completed');
