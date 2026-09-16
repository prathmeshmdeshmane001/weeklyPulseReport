# GitHub Actions Scheduler

This directory contains the automated scheduler for the Weekly Review Pulse pipeline.

## Workflow: `weekly-pulse.yml`

### Schedule

- **Automatic**: Every Sunday at 9:00 AM UTC (`0 9 * * 0`)
- **Manual**: Trigger anytime via GitHub Actions "Run workflow" button
- **Manual Options**: Can skip review fetching if needed

### Features

#### 1. **Dependency Caching**
- Python packages cached for faster execution
- Pip cache keyed by requirements

#### 2. **Step-by-Step Execution**
Each phase runs sequentially with detailed logging:
- Phase 3: Data Normalization
- Phase 4: Privacy Protection
- Phase 5: AI Theme Analysis (Groq)
- Phase 6: Theme Prioritization
- Phase 7: Action Generation (Groq)
- Phase 8: Weekly Pulse Composition (Groq)
- Phase 9: Google Docs MCP Delivery
- Phase 10: Gmail MCP Draft Creation
- Phase 11: End-to-End Validation
- Phase 12: Submission Summary

#### 3. **Visual Summaries**
Each step adds to GitHub Actions summary with:
- Phase status (✅/❌)
- Review counts
- Theme counts
- Document links
- Validation results

#### 4. **Notifications**
Optional notifications via:
- **Slack**: Add `SLACK_WEBHOOK_URL` secret
- **Discord**: Add `DISCORD_WEBHOOK_URL` secret

#### 5. **Artifacts**
All outputs preserved as downloadable artifacts:
- Weekly pulse JSON and Markdown
- Delivery status (Google Docs, Gmail)
- Validation reports
- Submission summaries

### Required Secrets

Configure in: Repository Settings → Secrets and variables → Actions

| Secret | Description | Required |
|--------|-------------|----------|
| `GROQ_API_KEY` | Groq API key for AI analysis | ✅ Yes |
| `GDOCS_DOC_ID` | Google Doc ID for publishing | ✅ Yes |
| `EMAIL_RECIPIENT` | Email recipient for Gmail draft | ✅ Yes |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | ❌ Optional |
| `DISCORD_WEBHOOK_URL` | Discord webhook for notifications | ❌ Optional |
| `GOOGLE_PLAY_API_KEY` | For live review fetching | ❌ Optional |
| `APP_STORE_API_KEY` | For live review fetching | ❌ Optional |

### Outputs

| Output | Description |
|--------|-------------|
| `pulse_date` | Date of generated pulse |
| `validation_status` | PASSED/FAILED/UNKNOWN |

### Usage

#### Automatic Execution
The workflow runs automatically every Sunday. No action needed.

#### Manual Execution
1. Go to GitHub repository
2. Click **Actions** tab
3. Select **"Weekly Review Pulse"** workflow
4. Click **"Run workflow"** button
5. Optionally check "Skip fetching new reviews"
6. Click **"Run workflow"** to confirm

#### Viewing Results
1. Click on the workflow run
2. View the **"Execution Summary"** section
3. Check individual phase statuses
4. Download artifacts if needed

### Troubleshooting

#### Workflow not running automatically
- Check if GitHub Actions is enabled in repository settings
- Verify the cron schedule is correct
- Check Actions tab for disabled workflows

#### Phase failures
- Check individual phase logs
- Verify all secrets are configured
- Ensure MCP server is accessible
- Check Groq API rate limits

#### Missing artifacts
- Artifacts expire after 30 days
- Check if workflow completed successfully
- Verify artifact upload step ran

### Customization

#### Change Schedule
Edit the cron expression in `weekly-pulse.yml`:
```yaml
schedule:
  - cron: '0 9 * * 0'  # Every Sunday 9am UTC
```

Common patterns:
- `0 9 * * 1` = Every Monday 9am UTC
- `0 0 * * *` = Every day at midnight UTC
- `0 */6 * * *` = Every 6 hours

#### Add More Notifications
The workflow supports Slack and Discord out of the box. To add more:
1. Add webhook secret
2. Add notification step in `notify` job

#### Skip Review Fetching
When running manually, check the "Skip fetching new reviews" option to use existing data.

### Architecture

```
GitHub Actions (Scheduled/Manual)
         |
         v
    Checkout Code
         |
         v
    Setup Python + Cache
         |
         v
    Execute Phases 3-12
         |
         v
    Commit Results
         |
         v
    Upload Artifacts
         |
         v
    Send Notifications
```

### Monitoring

- **GitHub Actions Tab**: View all runs and logs
- **Email Notifications**: GitHub sends emails on failure (if enabled)
- **Slack/Discord**: Real-time status updates (if configured)
- **Artifacts**: Download outputs from any run

### Security

- All sensitive data stored in GitHub Secrets
- Secrets never logged or exposed
- Workflow runs in isolated environment
- Artifacts automatically expire after 30 days
