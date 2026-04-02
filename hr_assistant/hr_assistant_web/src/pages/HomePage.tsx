import React from "react";
import { Link } from "react-router-dom";
import { Users, MessageSquare, TrendingUp, ShieldCheck } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { employeesApi } from "../services/api";

const HomePage: React.FC = () => {
  const { data } = useQuery({
    queryKey: ["employees-summary"],
    queryFn: () => employeesApi.list({ per_page: 1 }),
  });

  const stats = [
    {
      label: "Total Employees",
      value: data?.total ?? "—",
      icon: <Users className="w-6 h-6 text-primary-600" />,
      bg: "bg-primary-50",
    },
    {
      label: "Active Employees",
      value: "—",
      icon: <TrendingUp className="w-6 h-6 text-green-600" />,
      bg: "bg-green-50",
    },
    {
      label: "HR Policies",
      value: "Available",
      icon: <ShieldCheck className="w-6 h-6 text-purple-600" />,
      bg: "bg-purple-50",
    },
    {
      label: "AI Chat",
      value: "Online",
      icon: <MessageSquare className="w-6 h-6 text-blue-600" />,
      bg: "bg-blue-50",
    },
  ];

  const quickLinks = [
    {
      to: "/employees",
      title: "Manage Employees",
      description: "View, add, edit and remove employee records.",
      icon: <Users className="w-8 h-8 text-primary-600" />,
      cta: "Go to Employees",
    },
    {
      to: "/chat",
      title: "Ask the HR Assistant",
      description: "Get instant answers about HR policies, leave, and more.",
      icon: <MessageSquare className="w-8 h-8 text-blue-600" />,
      cta: "Start Chatting",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Hero */}
      <div className="bg-gradient-to-br from-primary-600 to-primary-800 rounded-2xl p-8 text-white">
        <h1 className="text-3xl font-bold mb-2">Welcome to HR Assistant</h1>
        <p className="text-primary-200 text-lg max-w-xl">
          Your AI-powered HR companion. Manage employees, answer policy questions,
          and streamline HR processes — all in one place.
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <div
            key={stat.label}
            className={`${stat.bg} rounded-xl p-4 flex items-center gap-3`}
          >
            <div>{stat.icon}</div>
            <div>
              <p className="text-xl font-bold text-gray-900">{stat.value}</p>
              <p className="text-xs text-gray-500">{stat.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Quick links */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {quickLinks.map((link) => (
          <Link
            key={link.to}
            to={link.to}
            className="block bg-white border border-gray-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow hover:border-primary-300 group"
          >
            <div className="mb-4">{link.icon}</div>
            <h2 className="text-lg font-semibold text-gray-900 mb-1">
              {link.title}
            </h2>
            <p className="text-gray-500 text-sm mb-4">{link.description}</p>
            <div className="inline-flex items-center text-sm font-medium text-primary-600 group-hover:text-primary-700 group-hover:underline">
              {link.cta} &rarr;
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default HomePage;
