import json
import html

import util


def format_duration(seconds):
    """Format duration in seconds to a human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{int(minutes)} minutes {remaining_seconds:.1f} seconds"


def generate_html(diff_file, pkey_list):
    """Generate HTML report from diff file"""
    with open(diff_file, "r") as f:
        data = json.load(f)

    diffs = data["diffs"]
    summary = data["summary"]

    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>ACE Table Diff Report</title>
        <style>
            :root {
                --primary-color: #0366d6;
                --success-color: #28a745;
                --warning-color: #ffc107;
                --danger-color: #dc3545;
                --text-primary: #24292e;
                --text-secondary: #586069;
                --bg-primary: #ffffff;
                --bg-secondary: #f6f8fa;
                --border-color: #e1e4e8;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
                line-height: 1.5;
                color: var(--text-primary);
                background-color: var(--bg-secondary);
            }

            .container {
                max-width: 1400px;
                margin: 2rem auto;
                padding: 0 1rem;
            }

            h1, h2 {
                color: var(--text-primary);
                font-weight: 600;
                margin-bottom: 1rem;
            }

            h1 {
                font-size: 2rem;
                padding-bottom: 0.5rem;
                border-bottom: 1px solid var(--border-color);
            }

            h2 {
                font-size: 1.5rem;
            }

            .summary-box {
                background: var(--bg-primary);
                border: 1px solid var(--border-color);
                border-radius: 6px;
                padding: 1.5rem;
                margin: 1.5rem 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            }

            .summary-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
            }

            .summary-item {
                padding: 1rem;
                background: var(--bg-secondary);
                border-radius: 6px;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }

            .summary-item:hover {
                transform: translateY(-2px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.08);
            }

            .summary-label {
                font-size: 0.875rem;
                font-weight: 500;
                color: var(--text-secondary);
                margin-bottom: 0.25rem;
            }

            .summary-value {
                font-size: 1.125rem;
                font-weight: 600;
                color: var(--text-primary);
            }

            .diff-section {
                background: var(--bg-primary);
                border: 1px solid var(--border-color);
                border-radius: 6px;
                margin: 1.5rem 0;
                overflow: hidden;
                box-shadow: 0 1px 3px rgba(0,0,0,0.04);
            }

            .diff-header {
                background: var(--primary-color);
                color: white;
                padding: 1rem 1.5rem;
                font-size: 1.125rem;
                font-weight: 500;
            }

            table {
                width: 100%;
                border-collapse: separate;
                border-spacing: 0;
                font-size: 0.875rem;
            }

            th {
                background: var(--bg-secondary);
                padding: 0.75rem 1rem;
                text-align: left;
                font-weight: 600;
                color: var(--text-secondary);
                border-bottom: 2px solid var(--border-color);
                position: sticky;
                top: 0;
                z-index: 10;
            }

            td {
                padding: 0.75rem 1rem;
                border-bottom: 1px solid var(--border-color);
                transition: background-color 0.15s ease;
            }

            tr:hover td {
                background-color: var(--bg-secondary);
            }

            .different {
                background-color: #ffeef0;
                color: var(--danger-color);
            }

            .different::before {
                position: absolute;
                left: 0.25rem;
                color: var(--danger-color);
                opacity: 0.5;
            }

            .key-column {
                font-weight: 600;
                color: var(--primary-color);
            }

            .missing {
                background-color: #fff8e6;
                color: #856404;
                font-style: italic;
            }

            .row-separator {
                background: var(--primary-color);
                color: white;
                font-weight: 500;
                text-align: center;
                padding: 0.75rem;
            }

            .row-divider {
                height: 0.5rem;
                background: var(--bg-secondary);
            }

            .row-subseparator {
                background: var(--bg-secondary);
                color: var(--text-secondary);
                font-weight: 500;
                text-align: center;
                padding: 0.5rem;
                font-size: 0.875rem;
            }

            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }

            .summary-item {
                animation: fadeIn 0.3s ease-out forwards;
            }

            .summary-item:nth-child(1) { animation-delay: 0.1s; }
            .summary-item:nth-child(2) { animation-delay: 0.2s; }
            .summary-item:nth-child(3) { animation-delay: 0.3s; }
            .summary-item:nth-child(4) { animation-delay: 0.4s; }
            .summary-item:nth-child(5) { animation-delay: 0.5s; }
            .summary-item:nth-child(6) { animation-delay: 0.6s; }

            @media (max-width: 768px) {
                .container {
                    padding: 0 0.5rem;
                }
                
                .summary-grid {
                    grid-template-columns: 1fr;
                }

                td, th {
                    padding: 0.5rem;
                }
            }
        </style>
    </head>
    """

    html_content += f"""
    <body>
        <div class="container">
            <h1>ACE Table Diff Report</h1>

            <!-- Summary Section -->
            <div class="summary-box">
                <h2>Summary</h2>
                <div class="summary-grid">
                    <div class="summary-item">
                        <div class="summary-label">Task ID</div>
                        <div class="summary-value">{summary['task_id']}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Table</div>
                        <div class="summary-value">
                            {summary['schema_name']}.{summary['table_name']}
                        </div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Total Rows Checked</div>
                        <div class="summary-value">
                            {summary['total_rows_checked']:,}
                        </div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Time Taken</div>
                        <div class="summary-value">
                            {format_duration(summary['time_taken'])}
                        </div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">Start Time</div>
                        <div class="summary-value">{summary['start_time']}</div>
                    </div>
                    <div class="summary-item">
                        <div class="summary-label">End Time</div>
                        <div class="summary-value">{summary['end_time']}</div>
                    </div>
                </div>
            </div>
    """

    # Add diff sections for each node pair
    for node_pair, pair_diffs in diffs.items():
        node1, node2 = node_pair.split("/")
        diff_count = summary["diff_count"][node_pair]

        # Get all possible columns from both nodes
        columns = set()
        for node_data in pair_diffs.values():
            for row in node_data:
                columns.update(row.keys())

        # Move key columns to front
        columns = sorted(list(columns))
        for key in pkey_list:
            if key in columns:
                columns.remove(key)
                columns.insert(0, key)

        html_content += f"""
            <div class="diff-section">
                <div class="diff-header">
                    Differences between {node1} and {node2} ({diff_count} differences)
                </div>
                <table>
                    <tr>
                        <th>Column</th>
                        <th>{node1}</th>
                        <th>{node2}</th>
                    </tr>
        """

        # Create sets of primary key values for each node
        def get_key_tuple(row):
            return tuple(str(row.get(key, "")) for key in pkey_list if key in columns)

        node1_keys = {get_key_tuple(row) for row in pair_diffs[node1]}
        node2_keys = {get_key_tuple(row) for row in pair_diffs[node2]}

        # Find missing rows
        missing_in_node2 = node1_keys - node2_keys
        missing_in_node1 = node2_keys - node1_keys
        common_keys = node1_keys & node2_keys

        # Create lookup dictionaries for faster access
        node1_rows = {get_key_tuple(row): row for row in pair_diffs[node1]}
        node2_rows = {get_key_tuple(row): row for row in pair_diffs[node2]}

        # First show rows that exist in both nodes but have differences
        if common_keys:
            html_content += (
                '<tr><td colspan="3" class="row-separator">'
                "Value Differences</td></tr>"
            )

            for i, key in enumerate(common_keys):
                if i > 0:  # Add separator between rows
                    html_content += '<tr><td colspan="3" class="row-divider"></td></tr>'

                row1 = node1_rows[key]
                row2 = node2_rows[key]

                for col in columns:
                    val1 = str(row1.get(col, ""))
                    val2 = str(row2.get(col, ""))
                    different = val1 != val2
                    is_key = col in pkey_list

                    html_content += f"""
                        <tr>
                            <td class="{
                                'key-column' if is_key else ''
                            }">{html.escape(col)}</td>
                            <td class="{
                                'different' if different else ''
                            }">{html.escape(val1)}</td>
                            <td class="{
                                'different' if different else ''
                            }">{html.escape(val2)}</td>
                        </tr>
                    """

        # Show all missing rows under one section
        if missing_in_node1 or missing_in_node2:
            html_content += (
                '<tr><td colspan="3" class="row-separator">'
                "Missing Rows</td></tr>"
            )

            # Show rows missing in node2
            if missing_in_node2:
                for i, key in enumerate(missing_in_node2):
                    if i > 0:  # Add separator between rows
                        html_content += (
                            '<tr><td colspan="3" class="row-divider"></td></tr>'
                        )

                    html_content += (
                        f'<tr><td colspan="3" class="row-subseparator">'
                        f"Missing in {node2}</td></tr>"
                    )

                    row1 = node1_rows[key]
                    for col in columns:
                        val1 = str(row1.get(col, ""))
                        is_key = col in pkey_list

                        html_content += f"""
                            <tr>
                                <td class="{
                                    'key-column' if is_key else ''
                                }">{html.escape(col)}</td>
                                <td>{html.escape(val1)}</td>
                                <td class="missing">MISSING</td>
                            </tr>
                        """

            # Show rows missing in node1
            if missing_in_node1:
                for i, key in enumerate(missing_in_node1):
                    if i > 0:  # Add separator between rows
                        html_content += (
                            '<tr><td colspan="3" class="row-divider"></td></tr>'
                        )

                    html_content += (
                        f'<tr><td colspan="3" class="row-subseparator">'
                        f"Missing in {node1}</td></tr>"
                    )

                    row2 = node2_rows[key]
                    for col in columns:
                        val2 = str(row2.get(col, ""))
                        is_key = col in pkey_list

                        html_content += f"""
                            <tr>
                                <td class="{
                                    'key-column' if is_key else ''
                                }">{html.escape(col)}</td>
                                <td class="missing">MISSING</td>
                                <td>{html.escape(val2)}</td>
                            </tr>
                        """

        html_content += "</table></div>"

    # Add CSS for missing rows
    style_additions = """
        .missing {
            background-color: #fff3cd;
            color: #856404;
            font-style: italic;
        }
        .row-separator {
            background-color: #e9ecef;
            font-weight: bold;
            text-align: center;
            padding: 8px;
            color: #495057;
        }
        .row-divider {
            height: 20px;
            background-color: #f8f9fa;
            border-top: 1px solid #dee2e6;
            border-bottom: 1px solid #dee2e6;
        }
        .row-subseparator {
            background-color: #f1f3f5;
            font-weight: bold;
            text-align: center;
            padding: 6px;
            color: #666;
            font-size: 0.9em;
        }
    """

    # Insert the new styles before the closing </style> tag
    html_content = html_content.replace("</style>", f"{style_additions}</style>")

    html_content += """
            </div>
        </body>
        </html>
    """

    output_file = diff_file.replace(".json", ".html")

    try:
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        util.message(
            f"HTML report generated: {util.set_colour(output_file, 'blue')}",
            p_state="info"
        )
    except Exception as e:
        util.exit_message(f"Error generating HTML report: {str(e)}")

    return output_file
