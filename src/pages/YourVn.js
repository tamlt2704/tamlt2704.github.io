import React from "react";
import Layout, { Content } from "antd/es/layout/layout";
import Sider from "antd/es/layout/Sider";
import { Menu, Breadcrumb } from "antd";
import { Link } from "react-router-dom";

import {
  UserOutlined,
  LaptopOutlined,
  NotificationOutlined,
} from "@ant-design/icons";

const items2 = [UserOutlined, LaptopOutlined, NotificationOutlined].map(
  (icon, index) => {
    const key = String(index + 1);
    return {
      key: `sub${key}`,
      icon: React.createElement(icon),
      label: `subnav ${key}`,
      children: new Array(4).fill(null).map((_, j) => {
        const subKey = index * 4 + j + 1;
        return {
          key: subKey,
          label: `option${subKey}`,
        };
      }),
    };
  }
);

export default function YourVn() {
  return (
    <Layout style={{ height: "100vh" }}>
      <Content style={{ padding: "0 48px", heigh: "100%" }}>
        <Breadcrumb style={{ margin: "16px 0" }}>
          <Breadcrumb.Item>Home</Breadcrumb.Item>
          <Breadcrumb.Item>List</Breadcrumb.Item>
          <Breadcrumb.Item>App</Breadcrumb.Item>
        </Breadcrumb>
        <Sider>
          <Menu items={items2} style={{ height: "100%" }}>
            {/* <Menu.Item>
              <Link to="/fakedata">
                <span>FakeData</span>
              </Link>
            </Menu.Item> */}
          </Menu>
        </Sider>
      </Content>
    </Layout>
  );
}
