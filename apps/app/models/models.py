from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, Numeric, String, Table, Text
from irails.database import Base
 
metadata = Base.metadata


class SysCodeGen(Base):
    __tablename__ = 'SysCodeGen'

    Id = Column(BigInteger, primary_key=True)
    MenuPid = Column(BigInteger, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    AuthorName = Column(String(32))
    TablePrefix = Column(String(8))
    GenerateType = Column(String(32))
    ConfigId = Column(String(64))
    DbName = Column(String(64))
    DbType = Column(String(64))
    ConnectionString = Column(String(256))
    TableName = Column(String(128))
    NameSpace = Column(String(128))
    BusName = Column(String(128))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysCodeGenConfig(Base):
    __tablename__ = 'SysCodeGenConfig'

    Id = Column(BigInteger, primary_key=True)
    CodeGenId = Column(BigInteger, nullable=False)
    ColumnName = Column(String(128), nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    ColumnComment = Column(String(128))
    NetType = Column(String(64))
    EffectType = Column(String(64))
    FkEntityName = Column(String(64))
    FkTableName = Column(String(128))
    FkColumnName = Column(String(64))
    FkColumnNetType = Column(String(64))
    DictTypeCode = Column(String(64))
    WhetherRetract = Column(String(8))
    WhetherRequired = Column(String(8))
    QueryWhether = Column(String(8))
    QueryType = Column(String(16))
    WhetherTable = Column(String(8))
    WhetherAddUpdate = Column(String(8))
    ColumnKey = Column(String(8))
    DataType = Column(String(64))
    WhetherCommon = Column(String(8))
    DisplayColumn = Column(Text)
    ValueColumn = Column(String(128))
    PidColumn = Column(String(128))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysConfig(Base):
    __tablename__ = 'SysConfig'

    Id = Column(BigInteger, primary_key=True)
    Name = Column(String(64), nullable=False)
    SysFlag = Column(Integer, nullable=False)
    OrderNo = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    Code = Column(String(64))
    Value = Column(String(64))
    GroupCode = Column(String(64))
    Remark = Column(String(256))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysDictData(Base):
    __tablename__ = 'SysDictData'

    Id = Column(BigInteger, primary_key=True)
    DictTypeId = Column(BigInteger, nullable=False)
    Value = Column(String(128), nullable=False)
    Code = Column(String(64), nullable=False)
    OrderNo = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    Remark = Column(String(128))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysDictType(Base):
    __tablename__ = 'SysDictType'

    Id = Column(BigInteger, primary_key=True)
    Name = Column(String(64), nullable=False)
    Code = Column(String(64), nullable=False)
    OrderNo = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    Remark = Column(String(256))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysFile(Base):
    __tablename__ = 'SysFile'

    Id = Column(BigInteger, primary_key=True)
    IsDelete = Column(Numeric, nullable=False)
    Provider = Column(String(128))
    BucketName = Column(String(128))
    FileName = Column(String(128))
    Suffix = Column(String(16))
    FilePath = Column(String(128))
    SizeKb = Column(String(16))
    SizeInfo = Column(String(64))
    Url = Column(String(128))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysJobCluster(Base):
    __tablename__ = 'SysJobCluster'

    Id = Column(BigInteger, primary_key=True)
    ClusterId = Column(String(64), nullable=False)
    Status = Column(Integer, nullable=False)
    Description = Column(String(128))
    UpdatedTime = Column(DateTime)


class SysJobDetail(Base):
    __tablename__ = 'SysJobDetail'

    Id = Column(BigInteger, primary_key=True)
    JobId = Column(String(64), nullable=False)
    Concurrent = Column(Numeric, nullable=False)
    annotation = Column(Numeric, nullable=False)
    CreateType = Column(Integer, nullable=False)
    GroupName = Column(String(128))
    JobType = Column(String(128))
    AssemblyName = Column(String(128))
    Description = Column(String(128))
    Properties = Column(Text)
    UpdatedTime = Column(DateTime)
    ScriptCode = Column(Text)


class SysJobTrigger(Base):
    __tablename__ = 'SysJobTrigger'

    Id = Column(BigInteger, primary_key=True)
    TriggerId = Column(String(64), nullable=False)
    JobId = Column(String(64), nullable=False)
    Status = Column(Integer, nullable=False)
    NumberOfRuns = Column(BigInteger, nullable=False)
    MaxNumberOfRuns = Column(BigInteger, nullable=False)
    NumberOfErrors = Column(BigInteger, nullable=False)
    MaxNumberOfErrors = Column(BigInteger, nullable=False)
    NumRetries = Column(Integer, nullable=False)
    RetryTimeout = Column(Integer, nullable=False)
    StartNow = Column(Numeric, nullable=False)
    RunOnStart = Column(Numeric, nullable=False)
    ResetOnlyOnce = Column(Numeric, nullable=False)
    TriggerType = Column(String(128))
    AssemblyName = Column(String(128))
    Args = Column(String(128))
    Description = Column(String(128))
    StartTime = Column(DateTime)
    EndTime = Column(DateTime)
    LastRunTime = Column(DateTime)
    NextRunTime = Column(DateTime)
    UpdatedTime = Column(DateTime)


class SysLogAudit(Base):
    __tablename__ = 'SysLogAudit'

    Id = Column(BigInteger, primary_key=True)
    TableName = Column(String(64), nullable=False)
    ColumnName = Column(String(64), nullable=False)
    Operate = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    NewValue = Column(Text)
    OldValue = Column(Text)
    AuditTime = Column(DateTime)
    Account = Column(String(32))
    RealName = Column(String(32))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysLogDiff(Base):
    __tablename__ = 'SysLogDiff'

    Id = Column(BigInteger, primary_key=True)
    IsDelete = Column(Numeric, nullable=False)
    BeforeData = Column(Text)
    AfterData = Column(Text)
    Sql = Column(Text)
    Parameters = Column(Text)
    BusinessData = Column(Text)
    DiffType = Column(Text)
    Elapsed = Column(BigInteger)
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysLogOp(Base):
    __tablename__ = 'SysLogOp'

    Id = Column(BigInteger, primary_key=True)
    IsDelete = Column(Numeric, nullable=False)
    HttpMethod = Column(String(32))
    RequestUrl = Column(Text)
    RequestParam = Column(Text)
    ReturnResult = Column(Text)
    EventId = Column(Integer)
    ThreadId = Column(Integer)
    TraceId = Column(String(128))
    Exception = Column(Text)
    Message = Column(Text)
    ControllerName = Column(String(256))
    ActionName = Column(String(256))
    DisplayTitle = Column(String(256))
    Status = Column(String(32))
    RemoteIp = Column(String(256))
    Location = Column(String(128))
    Longitude = Column(Float)
    Latitude = Column(Float)
    Browser = Column(String(1024))
    Os = Column(String(256))
    Elapsed = Column(BigInteger)
    LogDateTime = Column(DateTime)
    Account = Column(String(32))
    RealName = Column(String(32))
    TenantId = Column(BigInteger)
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysLogVis(Base):
    __tablename__ = 'SysLogVis'

    Id = Column(BigInteger, primary_key=True)
    IsDelete = Column(Numeric, nullable=False)
    ControllerName = Column(String(256))
    ActionName = Column(String(256))
    DisplayTitle = Column(String(256))
    Status = Column(String(32))
    RemoteIp = Column(String(256))
    Location = Column(String(128))
    Longitude = Column(Float)
    Latitude = Column(Float)
    Browser = Column(String(1024))
    Os = Column(String(256))
    Elapsed = Column(BigInteger)
    LogDateTime = Column(DateTime)
    Account = Column(String(32))
    RealName = Column(String(32))
    TenantId = Column(BigInteger)
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysMenu(Base):
    __tablename__ = 'SysMenu'

    Id = Column(BigInteger, primary_key=True)
    Pid = Column(BigInteger, nullable=False)
    Type = Column(Integer, nullable=False)
    Title = Column(String(64), nullable=False)
    IsIframe = Column(Numeric, nullable=False)
    IsHide = Column(Numeric, nullable=False)
    IsKeepAlive = Column(Numeric, nullable=False)
    IsAffix = Column(Numeric, nullable=False)
    OrderNo = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    Name = Column(String(64))
    Path = Column(String(128))
    Component = Column(String(128))
    Redirect = Column(String(128))
    Permission = Column(String(128))
    Icon = Column(String(128))
    OutLink = Column(String(256))
    Remark = Column(String(256))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysNotice(Base):
    __tablename__ = 'SysNotice'

    Id = Column(BigInteger, primary_key=True)
    Title = Column(String(32), nullable=False)
    Content = Column(Text, nullable=False)
    Type = Column(Integer, nullable=False)
    PublicUserId = Column(BigInteger, nullable=False)
    PublicOrgId = Column(BigInteger, nullable=False)
    Status = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    PublicUserName = Column(String(32))
    PublicOrgName = Column(String(64))
    PublicTime = Column(DateTime)
    CancelTime = Column(DateTime)
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


t_SysNoticeUser = Table(
    'SysNoticeUser', metadata,
    Column('NoticeId', BigInteger, nullable=False),
    Column('UserId', BigInteger, nullable=False),
    Column('ReadTime', DateTime),
    Column('ReadStatus', Integer, nullable=False)
)


class SysOnlineUser(Base):
    __tablename__ = 'SysOnlineUser'

    Id = Column(BigInteger, primary_key=True)
    UserId = Column(BigInteger, nullable=False)
    UserName = Column(String(32), nullable=False)
    ConnectionId = Column(String(255))
    RealName = Column(String(32))
    Time = Column(DateTime)
    Ip = Column(String(256))
    Browser = Column(String(128))
    Os = Column(String(128))
    TenantId = Column(BigInteger)


class SysOrg(Base):
    __tablename__ = 'SysOrg'

    Id = Column(BigInteger, primary_key=True)
    Pid = Column(BigInteger, nullable=False)
    Name = Column(String(64), nullable=False)
    OrderNo = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    Code = Column(String(64))
    Remark = Column(String(128))
    TenantId = Column(BigInteger)
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysPos(Base):
    __tablename__ = 'SysPos'

    Id = Column(BigInteger, primary_key=True)
    Name = Column(String(64), nullable=False)
    OrderNo = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    Code = Column(String(64))
    Remark = Column(String(128))
    TenantId = Column(BigInteger)
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysRegion(Base):
    __tablename__ = 'SysRegion'

    Id = Column(BigInteger, primary_key=True)
    Pid = Column(BigInteger, nullable=False)
    Name = Column(String(64), nullable=False)
    Level = Column(Integer, nullable=False)
    Lng = Column(Float, nullable=False)
    Lat = Column(Float, nullable=False)
    OrderNo = Column(Integer, nullable=False)
    ShortName = Column(String(32))
    MergerName = Column(String(64))
    Code = Column(String(32))
    ZipCode = Column(String(6))
    CityCode = Column(String(6))
    PinYin = Column(String(128))
    Remark = Column(String(128))


class SysRole(Base):
    __tablename__ = 'SysRole'

    Id = Column(BigInteger, primary_key=True)
    Name = Column(String(64), nullable=False)
    OrderNo = Column(Integer, nullable=False)
    DataScope = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    Code = Column(String(64))
    Remark = Column(String(128))
    TenantId = Column(BigInteger)
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysRoleMenu(Base):
    __tablename__ = 'SysRoleMenu'

    Id = Column(BigInteger, primary_key=True)
    RoleId = Column(BigInteger, nullable=False)
    MenuId = Column(BigInteger, nullable=False)


class SysRoleOrg(Base):
    __tablename__ = 'SysRoleOrg'

    Id = Column(BigInteger, primary_key=True)
    RoleId = Column(BigInteger, nullable=False)
    OrgId = Column(BigInteger, nullable=False)


class SysTenant(Base):
    __tablename__ = 'SysTenant'

    Id = Column(BigInteger, primary_key=True)
    UserId = Column(BigInteger, nullable=False)
    OrgId = Column(BigInteger, nullable=False)
    TenantType = Column(Integer, nullable=False)
    DbType = Column(Integer, nullable=False)
    OrderNo = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    Host = Column(String(128))
    Connection = Column(String(256))
    ConfigId = Column(String(64))
    Remark = Column(String(128))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysUser(Base):
    __tablename__ = 'SysUser'

    Id = Column(BigInteger, primary_key=True)
    Account = Column(String(32), nullable=False)
    Password = Column(String(512), nullable=False)
    RealName = Column(String(32), nullable=False)
    Sex = Column(Integer, nullable=False)
    Age = Column(Integer, nullable=False)
    CardType = Column(Integer, nullable=False)
    CultureLevel = Column(Integer, nullable=False)
    OrderNo = Column(Integer, nullable=False)
    Status = Column(Integer, nullable=False)
    AccountType = Column(Integer, nullable=False)
    OrgId = Column(BigInteger, nullable=False)
    PosId = Column(BigInteger, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    NickName = Column(String(32))
    Avatar = Column(String(512))
    Birthday = Column(DateTime)
    Nation = Column(String(32))
    Phone = Column(String(16))
    IdCardNum = Column(String(32))
    Email = Column(String(64))
    Address = Column(String(256))
    PoliticalOutlook = Column(String(16))
    College = Column(String(128))
    OfficePhone = Column(String(16))
    EmergencyContact = Column(String(32))
    EmergencyPhone = Column(String(16))
    EmergencyAddress = Column(String(256))
    Introduction = Column(String(512))
    Remark = Column(String(128))
    JobNum = Column(String(32))
    PosLevel = Column(String(32))
    JoinDate = Column(DateTime)
    LastLoginIp = Column(String(256))
    LastLoginAddress = Column(String(128))
    LastLoginTime = Column(DateTime)
    LastLoginDevice = Column(String(128))
    Signature = Column(String(512))
    TenantId = Column(BigInteger)
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysUserExtOrg(Base):
    __tablename__ = 'SysUserExtOrg'

    Id = Column(BigInteger, primary_key=True)
    UserId = Column(BigInteger, nullable=False)
    OrgId = Column(BigInteger, nullable=False)
    PosId = Column(BigInteger, nullable=False)
    JobNum = Column(String(32))
    PosLevel = Column(String(32))
    JoinDate = Column(DateTime)


class SysUserRole(Base):
    __tablename__ = 'SysUserRole'

    Id = Column(BigInteger, primary_key=True)
    UserId = Column(BigInteger, nullable=False)
    RoleId = Column(BigInteger, nullable=False)


class SysWechatPay(Base):
    __tablename__ = 'SysWechatPay'

    Id = Column(BigInteger, primary_key=True)
    MerchantId = Column(String(255), nullable=False)
    AppId = Column(String(255), nullable=False)
    OutTradeNumber = Column(String(255), nullable=False)
    TransactionId = Column(String(255), nullable=False)
    Total = Column(Integer, nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    TradeType = Column(String(255))
    TradeState = Column(String(255))
    TradeStateDescription = Column(String(255))
    BankType = Column(String(255))
    PayerTotal = Column(Integer)
    SuccessTime = Column(DateTime)
    ExpireTime = Column(DateTime)
    Description = Column(String(255))
    Scene = Column(String(255))
    Attachment = Column(String(255))
    GoodsTag = Column(String(255))
    Settlement = Column(String(255))
    NotifyUrl = Column(String(255))
    Remark = Column(String(255))
    OpenId = Column(String(255))
    SubMerchantId = Column(String(255))
    SubAppId = Column(String(255))
    SubOpenId = Column(String(255))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)


class SysWechatUser(Base):
    __tablename__ = 'SysWechatUser'

    Id = Column(BigInteger, primary_key=True)
    UserId = Column(BigInteger, nullable=False)
    PlatformType = Column(Integer, nullable=False)
    OpenId = Column(String(64), nullable=False)
    IsDelete = Column(Numeric, nullable=False)
    SessionKey = Column(String(256))
    UnionId = Column(String(64))
    NickName = Column(String(64))
    Avatar = Column(String(256))
    Mobile = Column(String(16))
    Sex = Column(Integer)
    Language = Column(String(64))
    City = Column(String(64))
    Province = Column(String(64))
    Country = Column(String(64))
    AccessToken = Column(Text)
    RefreshToken = Column(Text)
    ExpiresIn = Column(Integer)
    Scope = Column(String(64))
    CreateTime = Column(DateTime)
    UpdateTime = Column(DateTime)
    CreateUserId = Column(BigInteger)
    UpdateUserId = Column(BigInteger)
