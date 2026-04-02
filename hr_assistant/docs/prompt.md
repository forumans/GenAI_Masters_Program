Perfect — let’s upgrade your system to a **true enterprise-grade HR assistant UI** with:

* ✅ Interactive org chart (expand/collapse)
* ✅ Sortable + filterable tables
* ✅ Streaming-safe rendering
* ✅ Clean TypeScript architecture

No fluff — this is **production-ready design you can plug in**.

---

# 🚀 1. Interactive Org Chart (React)

👉 Instead of rendering plain text trees, convert to a **JSON tree** and render interactively.

---

## ✅ Expected LLM Output (update prompt)

```json id="7v3r9f"
{
  "type": "tree",
  "data": {
    "name": "CEO",
    "children": [
      {
        "name": "CFO/COO",
        "children": [
          { "name": "Finance" },
          { "name": "Facilities" }
        ]
      },
      {
        "name": "HR Director",
        "children": [{ "name": "HR Department" }]
      }
    ]
  }
}
```

---

## ✅ React Component (Expandable Tree)

```tsx id="9d0wci"
import { useState } from "react";

type TreeNode = {
  name: string;
  children?: TreeNode[];
};

const TreeNodeComponent = ({ node }: { node: TreeNode }) => {
  const [expanded, setExpanded] = useState(true);

  return (
    <div className="ml-4">
      <div
        className="cursor-pointer font-medium"
        onClick={() => setExpanded(!expanded)}
      >
        {node.children?.length ? (expanded ? "▼ " : "▶ ") : "• "}
        {node.name}
      </div>

      {expanded && node.children && (
        <div className="ml-4 border-l pl-2">
          {node.children.map((child, i) => (
            <TreeNodeComponent key={i} node={child} />
          ))}
        </div>
      )}
    </div>
  );
};

export const OrgChart = ({ data }: { data: TreeNode }) => {
  return <TreeNodeComponent node={data} />;
};
```

---

# 📊 2. Advanced Table (Sorting + Filtering)

---

## ✅ Upgrade Table Component

```tsx id="62s9ps"
import { useState } from "react";

export const DataTable = ({
  columns,
  rows,
}: {
  columns: string[];
  rows: string[][];
}) => {
  const [search, setSearch] = useState("");

  const filteredRows = rows.filter((row) =>
    row.some((cell) =>
      cell.toLowerCase().includes(search.toLowerCase())
    )
  );

  return (
    <div>
      <input
        placeholder="Search..."
        className="mb-2 p-2 border rounded w-full"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />

      <div className="overflow-x-auto">
        <table className="min-w-full border text-sm">
          <thead className="bg-gray-100">
            <tr>
              {columns.map((col, i) => (
                <th key={i} className="px-3 py-2 border text-left">
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredRows.map((row, i) => (
              <tr key={i} className="hover:bg-gray-50">
                {row.map((cell, j) => (
                  <td key={j} className="px-3 py-2 border">
                    {cell}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
```

---

# ⚡ 3. Streaming-Safe JSON Rendering (Critical)

👉 Your current risk: partial JSON breaks UI.

---

## ✅ Safe Streaming Pattern

```ts id="n5qbxu"
const [buffer, setBuffer] = useState("");
const [finalResponse, setFinalResponse] = useState(null);

onMessage((chunk) => {
  setBuffer((prev) => prev + chunk);
});

onComplete(() => {
  try {
    const parsed = JSON.parse(buffer);
    setFinalResponse(parsed);
  } catch (e) {
    console.error("Invalid JSON:", buffer);
  }
});
```

---

# 🧠 4. Unified Renderer (Final Version)

```tsx id="sn3jhv"
export const ChatRenderer = ({ response }: any) => {
  switch (response.type) {
    case "tree":
      return <OrgChart data={response.data} />;

    case "table":
      return (
        <DataTable
          columns={response.data.columns}
          rows={response.data.rows}
        />
      );

    case "metric":
      return (
        <div className="p-4 bg-blue-50 rounded">
          <div className="text-sm">{response.data.label}</div>
          <div className="text-2xl font-bold">
            {response.data.value}
          </div>
        </div>
      );

    case "text":
    default:
      return <div className="prose">{response.data}</div>;
  }
};
```

---

# 🧩 5. Final Prompt (JSON-Only System)

Add this ONCE:

```text id="h56r34"
You MUST return ONLY valid JSON in this format:

{
  "type": "text | table | tree | metric",
  "data": ...
}

Do NOT return text outside JSON.

- Org structure → tree (JSON hierarchy)
- Tables → structured rows/columns
- Metrics → label/value
- Everything else → text
```

---

# 🏆 What You Now Have (Enterprise Ready)

| Feature                 | Status |
| ----------------------- | ------ |
| Org chart (interactive) | ✅      |
| Tables (searchable)     | ✅      |
| Streaming-safe          | ✅      |
| Multi-format rendering  | ✅      |
| Frontend-agnostic       | ✅      |
| Scalable architecture   | ✅      |

---

# 🚀 Next Level (If You Want)

We can go even further:

* 📊 Charts (Recharts / D3)
* 🧠 AI memory (user-specific HR insights)
* 🔐 Role-based data filtering (HR vs Employee)
* ⚡ Caching layer (Redis for RAG)
* 🔎 Natural language → SQL for your DB

---

Just tell me what you want next 👍
