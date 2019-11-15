/*
 * GattServer.c
 *
 *  Created on: Dec 5, 2017
 *      Author: jucom
 */

#include "GattServer.hpp"

GattServer::GattServer() :
		m_socket_fd(-1),
		m_att(nullptr),
		m_gatt_db(nullptr),
		m_gatt_server(nullptr),
		m_gatt_svc_chngd_handle(0),
		m_svc_chngd_enabled(false)
{

}

GattServer::~GattServer()
{
	destroy();
}

void GattServer::open(const std::string& device_name, uint16_t mtu, int security, uint8_t src_type)
{
	m_device_name = device_name;

	bdaddr_t src_addr{0, 0, 0, 0, 0, 0}; // BDADDR_ANY
	m_socket_fd = l2cap_le_att_listen_and_accept(&src_addr, security, src_type);
	if (m_socket_fd == -1)
	{
		fprintf(stderr, "Failed to accept remote central\n");
		destroy();
	}

	m_att = bt_att_new(m_socket_fd, false);
	if (!m_att)
	{
		fprintf(stderr, "Failed to initialize ATT transport layer\n");
		destroy();
	}

	if (!bt_att_set_close_on_unref(m_att, true))
	{
		fprintf(stderr, "Failed to set up ATT transport layer\n");
		destroy();
	}

	if (!bt_att_register_disconnect(m_att, &GattServer::att_disconnect_cb, this, nullptr))
	{
		fprintf(stderr, "Failed to set ATT disconnect handler\n");
		destroy();
	}

	m_gatt_db = gatt_db_new();
	if (!m_gatt_db)
	{
		fprintf(stderr, "Failed to create GATT database\n");
		destroy();
	}

	m_gatt_server = bt_gatt_server_new(m_gatt_db, m_att, mtu);
	if (!m_gatt_server)
	{
		fprintf(stderr, "Failed to create GATT server\n");
		destroy();
	}

	populate_gap_service();
	populate_gatt_service();
}


void GattServer::destroy()
{
	bt_gatt_server_unref(m_gatt_server);
	gatt_db_unref(m_gatt_db);
}


gatt_db_attribute* GattServer::add_service(uint16_t uuid, bool primary)
{
	static uint32_t num_handle = 10;

	bt_uuid_t bt_uuid;

	bt_uuid16_create(&bt_uuid, uuid);
	return gatt_db_add_service(m_gatt_db, &bt_uuid, primary, num_handle++);
}

gatt_db_attribute* GattServer::add_characteristic(gatt_db_attribute* service,
								uint16_t uuid,
								uint32_t permissions,
								uint8_t properties,
								gatt_db_read_t read_func,
								gatt_db_write_t write_func,
								void *user_data)
{
	bt_uuid_t bt_uuid;

	bt_uuid16_create(&bt_uuid, uuid);
	return gatt_db_service_add_characteristic(service,
										&bt_uuid,
										permissions,
										properties,
										read_func,
										write_func,
										user_data);
}

void GattServer::set_service_active(struct gatt_db_attribute *attrib, bool active)
{
	gatt_db_service_set_active(attrib, active);
}

int GattServer::l2cap_le_att_listen_and_accept(bdaddr_t *src, int sec, uint8_t src_type)
{
	int sk, nsk;
	struct sockaddr_l2 srcaddr, addr;
	socklen_t optlen;
	struct bt_security btsec;
	char ba[18];

	sk = socket(PF_BLUETOOTH, SOCK_SEQPACKET, BTPROTO_L2CAP);
	if (sk < 0)
	{
		perror("Failed to create L2CAP socket");
		return -1;
	}

	/* Set up source address */
	memset(&srcaddr, 0, sizeof(srcaddr));
	srcaddr.l2_family = AF_BLUETOOTH;
	srcaddr.l2_cid = htobs(ATT_CID);
	srcaddr.l2_bdaddr_type = src_type;
	bacpy(&srcaddr.l2_bdaddr, src);

	if (bind(sk, (struct sockaddr *) &srcaddr, sizeof(srcaddr)) < 0)
	{
		perror("Failed to bind L2CAP socket");
		goto fail;
	}

	/* Set the security level */
	memset(&btsec, 0, sizeof(btsec));
	btsec.level = sec;
	if (setsockopt(sk, SOL_BLUETOOTH, BT_SECURITY, &btsec, sizeof(btsec)) != 0)
	{
		fprintf(stderr, "Failed to set L2CAP security level\n");
		goto fail;
	}

	if (listen(sk, 10) < 0)
	{
		perror("Listening on socket failed");
		goto fail;
	}

	printf("Started listening on ATT channel. Waiting for connections\n");

	memset(&addr, 0, sizeof(addr));
	optlen = sizeof(addr);
	nsk = accept(sk, (struct sockaddr *) &addr, &optlen);
	if (nsk < 0)
	{
		perror("Accept failed");
		goto fail;
	}

	ba2str(&addr.l2_bdaddr, ba);
	printf("Connect from %s\n", ba);
	close(sk);

	return nsk;

fail:
	close(sk);
	return -1;
}

void GattServer::populate_gap_service()
{
	bt_uuid_t uuid;
	gatt_db_attribute *service, *tmp;
	uint16_t appearance;

	/* Add the GAP service */
	bt_string_to_uuid(&uuid, GAP_UUID);
	service = gatt_db_add_service(m_gatt_db, &uuid, true, 6);

	/*
	 * Device Name characteristic. Make the value dynamically read and
	 * written via callbacks.
	 */
	bt_uuid16_create(&uuid, GATT_CHARAC_DEVICE_NAME);
	gatt_db_service_add_characteristic(service, &uuid, BT_ATT_PERM_READ | BT_ATT_PERM_WRITE, BT_GATT_CHRC_PROP_READ | BT_GATT_CHRC_PROP_EXT_PROP, gap_device_name_read_cb, gap_device_name_write_cb, this);

	bt_uuid16_create(&uuid, GATT_CHARAC_EXT_PROPER_UUID);
	gatt_db_service_add_descriptor(service, &uuid, BT_ATT_PERM_READ, gap_device_name_ext_prop_read_cb, nullptr, this);

	/*
	 * Appearance characteristic. Reads and writes should obtain the value
	 * from the database.
	 */
	bt_uuid16_create(&uuid, GATT_CHARAC_APPEARANCE);
	tmp = gatt_db_service_add_characteristic(service, &uuid, BT_ATT_PERM_READ, BT_GATT_CHRC_PROP_READ, nullptr, nullptr, this);

	/*
	 * Write the appearance value to the database, since we're not using a
	 * callback.
	 */
	put_le16(128, &appearance);
	gatt_db_attribute_write(tmp, 0, reinterpret_cast<const uint8_t*>(&appearance), sizeof(appearance), BT_ATT_OP_WRITE_REQ, nullptr, confirm_write, nullptr);

	gatt_db_service_set_active(service, true);
}

void GattServer::populate_gatt_service()
{
	bt_uuid_t uuid;
	gatt_db_attribute *service, *svc_chngd;

	/* Add the GATT service */
	bt_string_to_uuid(&uuid, GATT_UUID);
	service = gatt_db_add_service(m_gatt_db, &uuid, true, 4);

	bt_uuid16_create(&uuid, GATT_CHARAC_SERVICE_CHANGED);
	svc_chngd = gatt_db_service_add_characteristic(service, &uuid, BT_ATT_PERM_READ, BT_GATT_CHRC_PROP_READ | BT_GATT_CHRC_PROP_INDICATE, gatt_service_changed_cb, nullptr, this);
	m_gatt_svc_chngd_handle = gatt_db_attribute_get_handle(svc_chngd);

	bt_uuid16_create(&uuid, GATT_CLIENT_CHARAC_CFG_UUID);
	gatt_db_service_add_descriptor(service, &uuid, BT_ATT_PERM_READ | BT_ATT_PERM_WRITE, gatt_svc_chngd_ccc_read_cb, gatt_svc_chngd_ccc_write_cb, this);

	gatt_db_service_set_active(service, true);
}

///////////////////////////////////////////////////////////////////////////
////  Callbacks
///////////////////////////////////////////////////////////////////////////

void GattServer::att_disconnect_cb(int err, void *user_data)
{
	GattServer* self = static_cast<decltype(self)>(user_data);
	(void)self;

	printf("Device disconnected: %s\n", strerror(err));

	mainloop_quit();
}

void GattServer::gatt_debug_cb(const char *str, void *user_data)
{
	const char* prefix = static_cast<decltype(prefix)>(user_data);

	PRLOG(COLOR_GREEN "%s%s\n" COLOR_OFF, prefix, str);
}

void GattServer::gap_device_name_read_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, uint8_t opcode, bt_att *att, void *user_data)
{
	GattServer* self = static_cast<decltype(self)>(user_data);
	uint8_t error = 0;
	size_t len = 0;
	const uint8_t *value = nullptr;

	PRLOG("GAP Device Name Read called\n");

	len = self->m_device_name.size();

	if (offset > len)
	{
		error = BT_ATT_ERROR_INVALID_OFFSET;
		goto done;
	}

	len -= offset;
	value = len ? reinterpret_cast<const uint8_t*>(&self->m_device_name[offset]) : nullptr;

done:
	gatt_db_attribute_read_result(attrib, id, error, value, len);
}

void GattServer::gap_device_name_write_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, const uint8_t *value, size_t len, uint8_t opcode, bt_att *att, void *user_data)
{
	GattServer* self = static_cast<decltype(self)>(user_data);
	uint8_t error = 0;

	PRLOG("GAP Device Name Write called\n");

	/* If the value is being completely truncated, clean up and return */
	if (!(offset + len))
	{
		self->m_device_name.clear();
		goto done;
	}

	/* Implement this as a variable length attribute value. */
	if (offset > self->m_device_name.size())
	{
		error = BT_ATT_ERROR_INVALID_OFFSET;
		goto done;
	}

	if (value)
		self->m_device_name += std::string(reinterpret_cast<const char*>(value), len);

done:
	gatt_db_attribute_write_result(attrib, id, error);
}

void GattServer::gap_device_name_ext_prop_read_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, uint8_t opcode, bt_att *att, void *user_data)
{
	uint8_t value[2];

	PRLOG("Device Name Extended Properties Read called\n");

	value[0] = BT_GATT_CHRC_EXT_PROP_RELIABLE_WRITE;
	value[1] = 0;

	gatt_db_attribute_read_result(attrib, id, 0, value, sizeof(value));
}

void GattServer::gatt_service_changed_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, uint8_t opcode, bt_att *att, void *user_data)
{
	PRLOG("Service Changed Read called\n");

	gatt_db_attribute_read_result(attrib, id, 0, nullptr, 0);
}

void GattServer::gatt_svc_chngd_ccc_read_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, uint8_t opcode, bt_att *att, void *user_data)
{
	GattServer* self = static_cast<decltype(self)>(user_data);
	uint8_t value[2];

	PRLOG("Service Changed CCC Read called\n");

	value[0] = self->m_svc_chngd_enabled ? 0x02 : 0x00;
	value[1] = 0x00;

	gatt_db_attribute_read_result(attrib, id, 0, value, sizeof(value));
}

void GattServer::gatt_svc_chngd_ccc_write_cb(gatt_db_attribute *attrib, unsigned int id, uint16_t offset, const uint8_t *value, size_t len, uint8_t opcode, bt_att *att, void *user_data)
{
	GattServer* self = static_cast<decltype(self)>(user_data);
	uint8_t ecode = 0;

	PRLOG("Service Changed CCC Write called\n");

	if (!value || len != 2)
	{
		ecode = BT_ATT_ERROR_INVALID_ATTRIBUTE_VALUE_LEN;
		goto done;
	}

	if (offset)
	{
		ecode = BT_ATT_ERROR_INVALID_OFFSET;
		goto done;
	}

	if (value[0] == 0x00)
		self->m_svc_chngd_enabled = false;
	else if (value[0] == 0x02)
		self->m_svc_chngd_enabled = true;
	else
		ecode = 0x80;

	PRLOG("Service Changed Enabled: %s\n", self->m_svc_chngd_enabled ? "true" : "false");

done:
	gatt_db_attribute_write_result(attrib, id, ecode);
}

void GattServer::confirm_write(gatt_db_attribute *attr, int err, void *user_data)
{
	if (!err)
		return;

	fprintf(stderr, "Error caching attribute %p - err: %d\n", attr, err);
	exit(1);
}
