import { Header } from "antd/es/layout/layout";
import React from "react";
import { Menu } from "antd";
import { Link } from "react-router-dom";

const topItems = [
  { key: 1, label: "Your Vietnam" },
  { key: 2, label: "Fake Data" },
  { key: 3, label: "Showcases" },
];

export default function AppHeader() {
  return (
    <Header>
      <Menu theme="dark" mode="horizontal" defaultSelectedKeys={["1"]}>
        <Menu.Item key="1">
          <Link to="/">
            <span>Your Vietnam</span>
          </Link>
        </Menu.Item>
        <Menu.Item key="2">
          <Link to="/or101">
            <span>OR 101</span>
          </Link>
        </Menu.Item>
        <Menu.Item key="3">
          <Link to="/fakedata">
            <span>FakeData</span>
          </Link>
        </Menu.Item>
        <Menu.Item key="4">
          <Link to="/showcases">
            <span>Showcases</span>
          </Link>
        </Menu.Item>
      </Menu>
    </Header>
  );
}
