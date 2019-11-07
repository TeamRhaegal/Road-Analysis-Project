/*
 * GattServer.h
 *
 *  Created on: Dec 3, 2017
 *      Author: jucom
 */

#ifndef GATTSERVER_H_
#define GATTSERVER_H_

#include <cstdint>
#include <cstdbool>
#include <cstdlib>
#include <unistd.h>
#include <string>
#include <cstring>
#include <iostream>

#include <bluetooth/bluetooth.h>
#include <bluetooth/hci.h>
#include <bluetooth/hci_lib.h>
#include <bluetooth/l2cap.h>

#include "utils/prompt.h"

#ifdef __cplusplus
extern "C" {
#endif

#include "att.h"
#include "gatt-db.h"
#include "gatt-server.h"
#include "mainloop.h"
#include "util.h"

#ifdef __cplusplus
}
#endif

#define ATT_CID 4

class GattServer
{
public:

	GattServer();

	~GattServer();

	void open(const std::string& device_name, uint16_t mtu = BT_ATT_DEFAULT_LE_MTU, int security = BT_SECURITY_LOW, uint8_t src_type = BDADDR_LE_PUBLIC);

	void destroy();

	gatt_db_attribute* add_service(uint16_t uuid, bool primary = true);

	gatt_db_attribute* add_characteristic(gatt_db_attribute* service,
									uint16_t uuid,
									uint32_t permissions,
									uint8_t properties,
									gatt_db_read_t read_func,
									gatt_db_write_t write_func,
									void *user_data);

	void set_service_active(struct gatt_db_attribute *attrib, bool active);

private:

	int l2cap_le_att_listen_and_accept(bdaddr_t *src, int sec = BT_SECURITY_LOW, uint8_t src_type = BDADDR_LE_PUBLIC);

	void populate_gap_service();
	void populate_gatt_service();

	///////////////////////////////////////////////////////////////////////////
	////  Callbacks
	///////////////////////////////////////////////////////////////////////////
	static void att_disconnect_cb(int err, void *user_data);
	static void gatt_debug_cb(const char *str, void *user_data);
	static void gap_device_name_read_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, uint8_t opcode, struct bt_att *att, void *user_data);
	static void gap_device_name_write_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, const uint8_t *value, size_t len, uint8_t opcode, struct bt_att *att, void *user_data);
	static void gap_device_name_ext_prop_read_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, uint8_t opcode, struct bt_att *att, void *user_data);
	static void gatt_service_changed_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, uint8_t opcode, struct bt_att *att, void *user_data);
	static void gatt_svc_chngd_ccc_read_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, uint8_t opcode, struct bt_att *att, void *user_data);
	static void gatt_svc_chngd_ccc_write_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, const uint8_t *value, size_t len, uint8_t opcode, struct bt_att *att, void *user_data);
	static void confirm_write(gatt_db_attribute *attr, int err, void *user_data);

	int m_socket_fd;
	struct bt_att *m_att;
	struct gatt_db *m_gatt_db;
	
public:
	struct bt_gatt_server *m_gatt_server;
	std::string m_device_name;
	
private:
	uint16_t m_gatt_svc_chngd_handle;
	bool m_svc_chngd_enabled;
};

#endif /* GATTSERVER_H_ */
