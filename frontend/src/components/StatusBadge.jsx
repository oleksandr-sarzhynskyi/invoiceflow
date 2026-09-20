const LABELS = {
  processing: 'Processing',
  ready_for_approval: 'Ready for approval',
  review_required: 'Needs review',
  approved: 'Approved',
}

function StatusBadge({ status }) {
  return (
    <span className={`status-badge status-badge--${status}`}>
      {LABELS[status] || status}
    </span>
  )
}

export default StatusBadge